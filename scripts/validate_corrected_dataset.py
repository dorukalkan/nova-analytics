from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import polars as pl
import yaml


REQUIRED_INTERACTION_COLUMNS = [
    "Transaction_UUID",
    "User_ID",
    "Service_ID",
    "Timestamp",
    "Category",
    "Amount_USD",
    "Status",
    "Platform_User_Agent",
    "Referral_Source",
    "GPS_Lat",
    "GPS_Long",
    "Timestamp_dt",
    "Date",
    "Month",
    "Hour",
    "Market_ID",
    "Market_Name",
    "Region",
    "Acquisition_Source",
    "User_Segment",
    "Lifecycle_Segment",
    "Service_Tier",
    "Is_Promo_Period",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate corrected Nova parquet tables before BigQuery ingestion.")
    parser.add_argument("--config", default="config/nova_correction.yaml")
    parser.add_argument("--input-dir", default=None)
    parser.add_argument("--report-path", default=None)
    parser.add_argument("--strict", dest="strict", action="store_true", default=True)
    parser.add_argument("--no-strict", dest="strict", action="store_false")
    return parser.parse_args()


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def expected_dates(start: str, end: str) -> set[date]:
    start_dt = datetime.strptime(start, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end, "%Y-%m-%d").date()
    n_days = (end_dt - start_dt).days + 1
    return {start_dt + timedelta(days=offset) for offset in range(n_days)}


def pass_fail(condition: bool) -> str:
    return "PASS" if condition else "FAIL"


def as_markdown_table(df: pl.DataFrame, max_rows: int = 20) -> str:
    if df.height == 0:
        return "_No rows._"
    head = df.head(max_rows)
    columns = head.columns
    rows = head.rows()
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        values = [str(value).replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    config = load_config(Path(args.config))
    input_dir = Path(args.input_dir or config["paths"]["corrected_dir"])
    report_path = Path(args.report_path or config["paths"]["validation_report"])
    qa_dir = Path(config["paths"]["qa_dir"]) if args.input_dir is None else input_dir / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = input_dir / "_generation_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    expected_row_count = int(metadata.get("target_rows", config["target_rows"]))

    interaction_files = sorted((input_dir / "nova_interactions").glob("month=*/part-*.parquet"))
    if not interaction_files:
        raise SystemExit(f"No interaction parquet files found under {input_dir / 'nova_interactions'}")

    interactions = pl.scan_parquet([str(path) for path in interaction_files])
    users = pl.scan_parquet(input_dir / "nova_users.parquet")
    services = pl.scan_parquet(input_dir / "nova_services.parquet")
    markets = pl.scan_parquet(input_dir / "nova_markets.parquet")

    row_count = interactions.select(pl.len().alias("n")).collect().item()
    unique_transactions = interactions.select(pl.col("Transaction_UUID").n_unique()).collect().item()
    users_count = users.select(pl.len()).collect().item()

    missing_columns = [column for column in REQUIRED_INTERACTION_COLUMNS if column not in interactions.collect_schema().names()]
    nulls = (
        interactions.select([pl.col(column).null_count().alias(column) for column in REQUIRED_INTERACTION_COLUMNS if column not in missing_columns])
        .collect()
        .transpose(include_header=True, header_name="column", column_names=["null_count"])
    )
    total_nulls = int(nulls["null_count"].sum()) if nulls.height else 0

    dates = interactions.select(pl.col("Date").unique()).collect()["Date"].to_list()
    missing_dates = sorted(expected_dates(config["dates"]["start"], config["dates"]["end"]) - set(dates))

    category_mismatches = (
        interactions.select("Service_ID", "Category")
        .join(services.select("Service_ID", pl.col("Category").alias("Service_Category")), on="Service_ID", how="left")
        .select((pl.col("Category") != pl.col("Service_Category")).sum().alias("mismatches"))
        .collect()
        .item()
    )

    fk_user_missing = (
        interactions.select("User_ID")
        .join(users.select("User_ID"), on="User_ID", how="anti")
        .select(pl.len())
        .collect()
        .item()
    )
    fk_service_missing = (
        interactions.select("Service_ID")
        .join(services.select("Service_ID"), on="Service_ID", how="anti")
        .select(pl.len())
        .collect()
        .item()
    )

    active_users = interactions.select(pl.col("User_ID").n_unique()).collect().item()
    active_user_rate = active_users / users_count
    user_counts = interactions.group_by("User_ID").agg(pl.len().alias("n_transactions")).collect()
    repeat_user_rate = user_counts.filter(pl.col("n_transactions") > 1).height / users_count

    monthly = (
        interactions.group_by("Month")
        .agg(
            pl.len().alias("n_transactions"),
            pl.col("User_ID").n_unique().alias("active_users"),
            pl.col("Amount_USD").sum().alias("total_amount_usd"),
            (pl.col("Status") == "Completed").mean().alias("completion_rate"),
        )
        .sort("Month")
        .collect()
    )
    monthly.write_parquet(qa_dir / "monthly_kpis.parquet")

    category = (
        interactions.group_by("Category")
        .agg(
            pl.len().alias("n_transactions"),
            pl.col("User_ID").n_unique().alias("active_users"),
            pl.col("Amount_USD").mean().alias("avg_amount_usd"),
            pl.col("Amount_USD").median().alias("median_amount_usd"),
            (pl.col("Status") == "Completed").mean().alias("completion_rate"),
        )
        .sort("n_transactions", descending=True)
        .collect()
    )
    category.write_parquet(qa_dir / "category_kpis.parquet")

    status_platform = (
        interactions.group_by(["Category", "Platform_User_Agent"])
        .agg(
            pl.len().alias("n_transactions"),
            (pl.col("Status") == "Completed").mean().alias("completion_rate"),
            (pl.col("Status") == "Failed").mean().alias("failed_rate"),
            (pl.col("Status") == "Refunded").mean().alias("refunded_rate"),
        )
        .sort(["Category", "Platform_User_Agent"])
        .collect()
    )
    status_platform.write_parquet(qa_dir / "status_platform_kpis.parquet")

    hourly = (
        interactions.group_by(["Category", "Hour"])
        .agg(pl.len().alias("n_transactions"))
        .sort(["Category", "Hour"])
        .collect()
    )
    hourly.write_parquet(qa_dir / "hourly_category_kpis.parquet")

    service_counts = interactions.group_by("Service_ID").agg(pl.len().alias("n_transactions")).collect()
    top_n = max(1, int(service_counts.height * 0.01))
    top_1pct_share = service_counts.sort("n_transactions", descending=True).head(top_n)["n_transactions"].sum() / row_count

    market_geo = (
        interactions.select("Market_ID", "GPS_Lat", "GPS_Long")
        .join(markets.select("Market_ID", "Latitude", "Longitude"), on="Market_ID", how="left")
        .select(
            (pl.col("GPS_Lat") - pl.col("Latitude")).abs().max().alias("max_lat_jitter"),
            (pl.col("GPS_Long") - pl.col("Longitude")).abs().max().alias("max_long_jitter"),
        )
        .collect()
    )
    max_geo_jitter = max(float(market_geo["max_lat_jitter"][0]), float(market_geo["max_long_jitter"][0]))

    hourly_cv = (
        interactions.group_by("Hour")
        .agg(pl.len().alias("n"))
        .select((pl.col("n").std() / pl.col("n").mean()).alias("cv"))
        .collect()
        .item()
    )
    completion_spread_pct = (status_platform["completion_rate"].max() - status_platform["completion_rate"].min()) * 100
    category_amount_spread = category["avg_amount_usd"].max() - category["avg_amount_usd"].min()
    jan_rows = int(monthly.filter(pl.col("Month").dt.month() == 1)["n_transactions"][0])
    dec_rows = int(monthly.filter(pl.col("Month").dt.month() == 12)["n_transactions"][0])
    december_to_january_ratio = dec_rows / jan_rows

    thresholds = config["validation"]
    checks = [
        ("Exact target row count", row_count == expected_row_count, f"{row_count:,} / {expected_row_count:,}"),
        ("Unique Transaction_UUID", unique_transactions == row_count, f"{unique_transactions:,} unique"),
        ("All required columns present", not missing_columns, ", ".join(missing_columns) if missing_columns else "all present"),
        ("Zero nulls in required columns", total_nulls == 0, f"{total_nulls:,} nulls"),
        ("Full date coverage", not missing_dates, f"{len(missing_dates)} missing dates"),
        ("Category matches service category", category_mismatches == 0, f"{category_mismatches:,} mismatches"),
        ("User FK coverage", fk_user_missing == 0, f"{fk_user_missing:,} missing"),
        ("Service FK coverage", fk_service_missing == 0, f"{fk_service_missing:,} missing"),
        (
            "Annual active user rate",
            thresholds["active_user_rate_min"] <= active_user_rate <= thresholds["active_user_rate_max"],
            f"{active_user_rate:.2%}",
        ),
        ("Lifetime repeat user rate", repeat_user_rate <= thresholds["repeat_user_rate_max"], f"{repeat_user_rate:.2%}"),
        (
            "Category amount spread",
            category_amount_spread >= thresholds["min_category_amount_mean_spread_usd"],
            f"${category_amount_spread:,.2f}",
        ),
        (
            "Completion rate spread",
            completion_spread_pct >= thresholds["min_completion_rate_spread_pct_points"],
            f"{completion_spread_pct:.2f} pp",
        ),
        ("Hourly CV", hourly_cv >= thresholds["min_hourly_cv"], f"{hourly_cv:.2%}"),
        (
            "December/January volume ratio",
            december_to_january_ratio >= thresholds["min_december_to_january_ratio"],
            f"{december_to_january_ratio:.2f}x",
        ),
        (
            "Top 1pct service share",
            thresholds["top_1pct_service_share_min"] <= top_1pct_share <= thresholds["top_1pct_service_share_max"],
            f"{top_1pct_share:.2%}",
        ),
        (
            "Market GPS jitter bounds",
            max_geo_jitter <= thresholds["max_market_jitter_degrees"],
            f"{max_geo_jitter:.3f} degrees",
        ),
    ]

    checks_df = pl.DataFrame(
        {
            "check": [name for name, _, _ in checks],
            "status": [pass_fail(ok) for _, ok, _ in checks],
            "detail": [detail for _, _, detail in checks],
        }
    )
    checks_df.write_csv(qa_dir / "validation_checks.csv")

    final_status = "PASS" if all(ok for _, ok, _ in checks) else "FAIL"
    report = f"""# Corrected Nova Dataset Validation

Generated validation status: **{final_status}**

Input directory: `{input_dir}`

Expected rows: `{expected_row_count:,}`

Actual rows: `{row_count:,}`

## BigQuery readiness checks

{as_markdown_table(checks_df, max_rows=50)}

## Monthly KPIs

{as_markdown_table(monthly)}

## Category KPIs

{as_markdown_table(category)}

## Status by category and platform

{as_markdown_table(status_platform, max_rows=30)}

## Notes

- BigQuery should ingest corrected parquet files from `{input_dir}`, not `data/raw/`.
- QA parquet and CSV outputs are written under `{qa_dir}`.
- Use strict mode for final readiness. Smoke runs can use `--no-strict` when row count or active-user thresholds are intentionally scaled down.
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(report)

    if args.strict and final_status != "PASS":
        raise SystemExit("Corrected dataset validation failed.")


if __name__ == "__main__":
    main()
