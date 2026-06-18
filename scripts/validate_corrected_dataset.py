from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
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


def schema_map(scan: pl.LazyFrame) -> dict[str, str]:
    schema = scan.collect_schema()
    return {name: str(dtype) for name, dtype in zip(schema.names(), schema.dtypes())}


def weather_sensitivity_diagnostics(interactions: pl.LazyFrame, config: dict) -> pl.DataFrame:
    empty_columns = {
        "Category": [],
        "bad_weather_days": [],
        "normal_weather_days": [],
        "bad_weather_avg_transactions": [],
        "normal_weather_avg_transactions": [],
        "bad_weather_transaction_lift": [],
        "bad_weather_avg_gmv_usd": [],
        "normal_weather_avg_gmv_usd": [],
        "bad_weather_gmv_lift": [],
        "bad_weather_avg_amount_usd": [],
        "normal_weather_avg_amount_usd": [],
        "bad_weather_avg_amount_lift": [],
        "bad_weather_completion_rate": [],
        "normal_weather_completion_rate": [],
        "bad_weather_completion_delta": [],
    }
    weather_path = Path(config["paths"].get("weather_seed", "nova/seeds/ext_weather_daily.csv"))
    if not weather_path.exists():
        return pl.DataFrame(empty_columns)

    weather = (
        pl.read_csv(weather_path, try_parse_dates=True)
        .with_columns(
            [
                pl.col("precipitation_sum_mm").fill_null(0.0),
                pl.col("wind_speed_10m_max_kmh").fill_null(0.0),
                pl.col("temperature_2m_mean_c").fill_null(strategy="mean"),
            ]
        )
    )
    monthly = weather.with_columns(pl.col("weather_date").dt.strftime("%Y-%m").alias("month_key")).group_by(["market_id", "month_key"]).agg(
        pl.col("temperature_2m_mean_c").quantile(0.10).alias("month_temp_p10"),
        pl.col("temperature_2m_mean_c").quantile(0.90).alias("month_temp_p90"),
    )
    market_quantiles = weather.group_by("market_id").agg(
        pl.col("precipitation_sum_mm").quantile(0.70).alias("market_precip_p70"),
        pl.col("precipitation_sum_mm").quantile(0.90).alias("market_precip_p90"),
        pl.col("wind_speed_10m_max_kmh").quantile(0.90).alias("market_wind_p90"),
    )
    weather_flags = (
        weather.with_columns(pl.col("weather_date").dt.strftime("%Y-%m").alias("month_key"))
        .join(monthly, on=["market_id", "month_key"], how="left")
        .join(market_quantiles, on="market_id", how="left")
        .with_columns(
            [
                (
                    pl.col("is_rain_day")
                    & (pl.col("precipitation_sum_mm") >= pl.max_horizontal(pl.col("market_precip_p70"), pl.lit(3.0)))
                    & (pl.col("precipitation_sum_mm") < pl.max_horizontal(pl.col("market_precip_p90"), pl.lit(8.0)))
                ).alias("is_moderate_rain"),
                (pl.col("precipitation_sum_mm") >= pl.max_horizontal(pl.col("market_precip_p90"), pl.lit(8.0))).alias("is_heavy_rain"),
                (pl.col("temperature_2m_mean_c") >= pl.col("month_temp_p90")).alias("is_extreme_heat"),
                (pl.col("temperature_2m_mean_c") <= pl.col("month_temp_p10")).alias("is_extreme_cold"),
                (pl.col("wind_speed_10m_max_kmh") >= pl.max_horizontal(pl.col("market_wind_p90"), pl.lit(28.0))).alias("is_high_wind"),
            ]
        )
        .with_columns(
            (
                pl.col("is_heavy_rain")
                | pl.col("is_extreme_heat")
                | pl.col("is_extreme_cold")
                | pl.col("is_high_wind")
            ).alias("is_bad_weather_day")
        )
        .select(
            pl.col("market_id").alias("Market_ID"),
            pl.col("weather_date").alias("Date"),
            "is_moderate_rain",
            "is_heavy_rain",
            "is_extreme_heat",
            "is_extreme_cold",
            "is_high_wind",
            "is_bad_weather_day",
        )
    )

    daily = (
        interactions.group_by(["Market_ID", "Category", "Date"])
        .agg(
            pl.len().alias("n_transactions"),
            pl.col("Amount_USD").sum().alias("total_amount_usd"),
            pl.col("Amount_USD").mean().alias("avg_amount_usd"),
            (pl.col("Status") == "Completed").mean().alias("completion_rate"),
        )
        .collect()
    )
    return (
        daily.join(weather_flags, on=["Market_ID", "Date"], how="left")
        .with_columns(pl.col("is_bad_weather_day").fill_null(False))
        .group_by("Category")
        .agg(
            pl.col("n_transactions").filter(pl.col("is_bad_weather_day")).count().alias("bad_weather_days"),
            pl.col("n_transactions").filter(~pl.col("is_bad_weather_day")).count().alias("normal_weather_days"),
            pl.col("n_transactions").filter(pl.col("is_bad_weather_day")).mean().alias("bad_weather_avg_transactions"),
            pl.col("n_transactions").filter(~pl.col("is_bad_weather_day")).mean().alias("normal_weather_avg_transactions"),
            pl.col("total_amount_usd").filter(pl.col("is_bad_weather_day")).mean().alias("bad_weather_avg_gmv_usd"),
            pl.col("total_amount_usd").filter(~pl.col("is_bad_weather_day")).mean().alias("normal_weather_avg_gmv_usd"),
            pl.col("avg_amount_usd").filter(pl.col("is_bad_weather_day")).mean().alias("bad_weather_avg_amount_usd"),
            pl.col("avg_amount_usd").filter(~pl.col("is_bad_weather_day")).mean().alias("normal_weather_avg_amount_usd"),
            pl.col("completion_rate").filter(pl.col("is_bad_weather_day")).mean().alias("bad_weather_completion_rate"),
            pl.col("completion_rate").filter(~pl.col("is_bad_weather_day")).mean().alias("normal_weather_completion_rate"),
        )
        .with_columns(
            [
                (
                    (pl.col("bad_weather_avg_transactions") - pl.col("normal_weather_avg_transactions"))
                    / pl.col("normal_weather_avg_transactions")
                ).alias("bad_weather_transaction_lift"),
                (
                    (pl.col("bad_weather_avg_gmv_usd") - pl.col("normal_weather_avg_gmv_usd"))
                    / pl.col("normal_weather_avg_gmv_usd")
                ).alias("bad_weather_gmv_lift"),
                (
                    (pl.col("bad_weather_avg_amount_usd") - pl.col("normal_weather_avg_amount_usd"))
                    / pl.col("normal_weather_avg_amount_usd")
                ).alias("bad_weather_avg_amount_lift"),
                (pl.col("bad_weather_completion_rate") - pl.col("normal_weather_completion_rate")).alias(
                    "bad_weather_completion_delta"
                ),
            ]
        )
        .sort("Category")
    )


def fraud_behavior_diagnostics(interactions: pl.LazyFrame) -> dict[str, float]:
    def scalar_value(frame: pl.DataFrame, column: str, default: float = 0.0) -> float:
        value = frame[column][0]
        return float(default if value is None else value)

    user_hour = (
        interactions.group_by(["User_ID", "Date", "Hour"])
        .agg(
            pl.len().alias("n_transactions"),
            (pl.col("Status") != "Completed").sum().alias("non_complete_transactions"),
        )
        .collect()
    )
    burst_user_hour = user_hour.filter(pl.col("n_transactions") >= 3)
    normal_user_hour = user_hour.filter(pl.col("n_transactions") < 3)
    burst_transactions = int(burst_user_hour["n_transactions"].sum() or 0)
    burst_non_complete_rate = (
        float(burst_user_hour["non_complete_transactions"].sum() or 0) / burst_transactions if burst_transactions else 0.0
    )
    normal_transactions = int(normal_user_hour["n_transactions"].sum() or 0)
    normal_user_hour_non_complete_rate = (
        float(normal_user_hour["non_complete_transactions"].sum() or 0) / normal_transactions if normal_transactions else 0.0
    )
    row_count = interactions.select(pl.len()).collect().item()
    burst_share = burst_transactions / row_count

    category_thresholds = interactions.group_by("Category").agg(pl.col("Amount_USD").quantile(0.99).alias("p99_amount")).collect()
    high_amount = (
        interactions.join(category_thresholds.lazy(), on="Category", how="left")
        .with_columns((pl.col("Amount_USD") >= pl.col("p99_amount")).alias("is_high_amount"))
    )
    non_complete_rate = interactions.select((pl.col("Status") != "Completed").mean()).collect().item()
    high_amount_non_complete_rate = (
        high_amount.filter(pl.col("is_high_amount"))
        .select((pl.col("Status") != "Completed").mean())
        .collect()
        .item()
    )
    signal_rows = (
        high_amount.join(
            user_hour.select(["User_ID", "Date", "Hour", "n_transactions"]).lazy(),
            on=["User_ID", "Date", "Hour"],
            how="left",
        )
        .with_columns(
            [
                (pl.col("n_transactions") >= 3).alias("is_high_velocity_user_hour"),
                (pl.col("Status") != "Completed").alias("is_non_complete"),
                (
                    (pl.col("User_Segment") == "New")
                    | (pl.col("Lifecycle_Segment") == "At Risk")
                ).alias("is_new_or_at_risk"),
                pl.col("Category").is_in(["Digital Wallet", "E-Commerce"]).alias("is_signal_category"),
                pl.col("Platform_User_Agent").str.contains("Web Portal|Nova Lite").alias("is_web_or_lite"),
                pl.col("Referral_Source").is_in(["Social Ad", "Email Promo", "Push Notification"]).alias("is_promo_referral"),
            ]
        )
        .with_columns(
            (
                (pl.col("is_high_velocity_user_hour") | (pl.col("is_high_amount") & pl.col("is_signal_category")))
                & (
                    pl.col("is_non_complete")
                    | pl.col("is_new_or_at_risk")
                    | pl.col("is_web_or_lite")
                    | pl.col("is_promo_referral")
                )
            ).alias("is_suspicious_proxy")
        )
    )
    signal_summary = signal_rows.select(
        pl.col("is_suspicious_proxy").mean().alias("proxy_suspicious_share"),
        pl.col("is_web_or_lite").filter(pl.col("is_suspicious_proxy")).mean().alias("proxy_web_lite_share"),
        pl.col("is_web_or_lite").filter(~pl.col("is_suspicious_proxy")).mean().alias("baseline_web_lite_share"),
        pl.col("is_promo_referral").filter(pl.col("is_suspicious_proxy")).mean().alias("proxy_promo_referral_share"),
        pl.col("is_promo_referral").filter(~pl.col("is_suspicious_proxy")).mean().alias("baseline_promo_referral_share"),
        pl.col("is_non_complete").filter(pl.col("is_high_amount") & pl.col("is_new_or_at_risk")).mean().alias(
            "new_at_risk_high_amount_non_complete_rate"
        ),
        pl.col("is_non_complete").filter(pl.col("is_high_amount") & ~pl.col("is_new_or_at_risk")).mean().alias(
            "other_high_amount_non_complete_rate"
        ),
        pl.col("is_suspicious_proxy").filter(pl.col("Category") == "Digital Wallet").mean().alias("digital_wallet_proxy_share"),
        pl.col("is_suspicious_proxy").filter(pl.col("Category") == "E-Commerce").mean().alias("ecommerce_proxy_share"),
        pl.col("is_suspicious_proxy").filter(~pl.col("Category").is_in(["Digital Wallet", "E-Commerce"])).mean().alias(
            "other_category_proxy_share"
        ),
    ).collect()
    return {
        "burst_share": float(burst_share),
        "burst_non_complete_rate": float(burst_non_complete_rate),
        "normal_user_hour_non_complete_rate": float(normal_user_hour_non_complete_rate),
        "non_complete_rate": float(non_complete_rate),
        "high_amount_non_complete_rate": float(high_amount_non_complete_rate),
        "proxy_suspicious_share": scalar_value(signal_summary, "proxy_suspicious_share"),
        "proxy_web_lite_share": scalar_value(signal_summary, "proxy_web_lite_share"),
        "baseline_web_lite_share": scalar_value(signal_summary, "baseline_web_lite_share"),
        "proxy_promo_referral_share": scalar_value(signal_summary, "proxy_promo_referral_share"),
        "baseline_promo_referral_share": scalar_value(signal_summary, "baseline_promo_referral_share"),
        "new_at_risk_high_amount_non_complete_rate": scalar_value(
            signal_summary, "new_at_risk_high_amount_non_complete_rate"
        ),
        "other_high_amount_non_complete_rate": scalar_value(signal_summary, "other_high_amount_non_complete_rate"),
        "digital_wallet_proxy_share": scalar_value(signal_summary, "digital_wallet_proxy_share"),
        "ecommerce_proxy_share": scalar_value(signal_summary, "ecommerce_proxy_share"),
        "other_category_proxy_share": scalar_value(signal_summary, "other_category_proxy_share"),
    }


def realism_diagnostics(interactions: pl.LazyFrame, users: pl.LazyFrame, qa_dir: Path) -> dict[str, float]:
    user_activity = (
        interactions.group_by("User_ID")
        .agg(
            pl.len().alias("n_transactions"),
            pl.col("Amount_USD").sum().alias("total_amount_usd"),
            pl.col("Category").n_unique().alias("n_categories"),
            (pl.col("Status") != "Completed").sum().alias("non_completed_transactions"),
        )
        .collect()
    )
    customer_behavior = (
        users.collect()
        .join(user_activity, on="User_ID", how="left")
        .with_columns(
            pl.col("n_transactions").fill_null(0),
            pl.col("total_amount_usd").fill_null(0),
            pl.col("n_categories").fill_null(0),
            pl.col("non_completed_transactions").fill_null(0),
        )
        .with_columns(
            pl.when(pl.col("n_transactions") > 0)
            .then(pl.col("non_completed_transactions") / pl.col("n_transactions"))
            .otherwise(None)
            .alias("non_completion_rate")
        )
        .group_by(["User_Segment", "Lifecycle_Segment", "Membership_Tier"])
        .agg(
            pl.len().alias("users"),
            pl.col("n_transactions").mean().alias("avg_transactions"),
            pl.col("total_amount_usd").mean().alias("avg_total_amount_usd"),
            pl.col("n_categories").mean().alias("avg_categories"),
            pl.col("non_completion_rate").mean().alias("avg_non_completion_rate"),
        )
        .sort(["User_Segment", "Lifecycle_Segment", "Membership_Tier"])
    )
    customer_behavior.write_parquet(qa_dir / "customer_behavior_kpis.parquet")
    customer_spread = (
        customer_behavior.filter(pl.col("User_Segment").is_in(["Casual", "Regular", "Power"]))
        .group_by("User_Segment")
        .agg(
            (
                (pl.col("avg_transactions").max() - pl.col("avg_transactions").min())
                / pl.col("avg_transactions").mean()
            ).alias("avg_transaction_range_pct"),
            (pl.col("avg_non_completion_rate").max() - pl.col("avg_non_completion_rate").min()).alias("non_completion_range"),
        )
    )
    min_customer_activity_spread = float(customer_spread["avg_transaction_range_pct"].min()) if customer_spread.height else 0.0
    max_customer_non_completion_spread = float(customer_spread["non_completion_range"].max()) if customer_spread.height else 0.0

    market_category = (
        interactions.group_by(["Market_ID", "Market_Name", "Category"])
        .agg(
            pl.len().alias("n_transactions"),
            pl.col("Amount_USD").mean().alias("avg_amount_usd"),
            (pl.col("Status") == "Completed").mean().alias("completion_rate"),
        )
        .with_columns((pl.col("n_transactions") / pl.col("n_transactions").sum().over("Market_ID")).alias("market_category_share"))
        .collect()
    )
    market_category.write_parquet(qa_dir / "market_category_behavior_kpis.parquet")
    category_share_spread = market_category.group_by("Category").agg(pl.col("market_category_share").std().alias("share_std"))
    mean_category_share_std = float(category_share_spread["share_std"].mean()) if category_share_spread.height else 0.0
    min_category_share_std = float(category_share_spread["share_std"].min()) if category_share_spread.height else 0.0
    market_amount_status_spread = market_category.group_by("Category").agg(
        pl.col("avg_amount_usd").std().alias("amount_std"),
        pl.col("completion_rate").std().alias("completion_std"),
    )
    mean_market_amount_std = float(market_amount_status_spread["amount_std"].mean()) if market_amount_status_spread.height else 0.0
    mean_market_completion_std = float(market_amount_status_spread["completion_std"].mean()) if market_amount_status_spread.height else 0.0

    market_monthly = (
        interactions.group_by(["Market_ID", "Month"])
        .agg(pl.len().alias("n_transactions"))
        .sort(["Market_ID", "Month"])
        .collect()
    )
    months = market_monthly["Month"].unique().sort().to_list()
    market_ids = market_monthly["Market_ID"].unique().sort().to_list()
    matrix = np.zeros((len(months), len(market_ids)), dtype=np.float64)
    month_index = {month: idx for idx, month in enumerate(months)}
    market_index = {market_id: idx for idx, market_id in enumerate(market_ids)}
    for row in market_monthly.iter_rows(named=True):
        matrix[month_index[row["Month"]], market_index[row["Market_ID"]]] = float(row["n_transactions"])
    correlations: list[float] = []
    if matrix.shape[1] >= 2:
        corr = np.corrcoef(matrix.T)
        for i in range(corr.shape[0]):
            for j in range(i + 1, corr.shape[1]):
                if not np.isnan(corr[i, j]):
                    correlations.append(float(corr[i, j]))
    median_market_monthly_corr = float(np.median(correlations)) if correlations else 1.0
    max_market_monthly_corr = float(np.max(correlations)) if correlations else 1.0

    return {
        "min_customer_activity_spread": min_customer_activity_spread,
        "max_customer_non_completion_spread": max_customer_non_completion_spread,
        "mean_category_share_std": mean_category_share_std,
        "min_category_share_std": min_category_share_std,
        "mean_market_amount_std": mean_market_amount_std,
        "mean_market_completion_std": mean_market_completion_std,
        "median_market_monthly_corr": median_market_monthly_corr,
        "max_market_monthly_corr": max_market_monthly_corr,
    }


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
    single_interactions_path = input_dir / "nova_interactions.parquet"
    single_interactions = pl.scan_parquet(single_interactions_path) if single_interactions_path.exists() else None
    users = pl.scan_parquet(input_dir / "nova_users.parquet")
    services = pl.scan_parquet(input_dir / "nova_services.parquet")
    markets = pl.scan_parquet(input_dir / "nova_markets.parquet")

    row_count = interactions.select(pl.len().alias("n")).collect().item()
    single_row_count = single_interactions.select(pl.len().alias("n")).collect().item() if single_interactions is not None else 0
    unique_transactions = interactions.select(pl.col("Transaction_UUID").n_unique()).collect().item()
    users_count = users.select(pl.len()).collect().item()

    interaction_schema = schema_map(interactions)
    single_schema = schema_map(single_interactions) if single_interactions is not None else {}
    missing_columns = [column for column in REQUIRED_INTERACTION_COLUMNS if column not in interaction_schema]
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

    if single_interactions is not None:
        single_monthly = (
            single_interactions.group_by("Month")
            .agg(
                pl.len().alias("single_n_transactions"),
                pl.col("Amount_USD").sum().alias("single_total_amount_usd"),
            )
            .sort("Month")
            .collect()
        )
        monthly_parity = monthly.select("Month", "n_transactions", "total_amount_usd").join(single_monthly, on="Month", how="full", coalesce=True)
        max_single_month_row_diff = int((pl.Series(monthly_parity["n_transactions"]) - pl.Series(monthly_parity["single_n_transactions"])).abs().max())
        max_single_month_amount_diff = float((pl.Series(monthly_parity["total_amount_usd"]) - pl.Series(monthly_parity["single_total_amount_usd"])).abs().max())
    else:
        monthly_parity = pl.DataFrame()
        max_single_month_row_diff = row_count
        max_single_month_amount_diff = float("inf")

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

    weather_diagnostics = weather_sensitivity_diagnostics(interactions, config) if metadata.get("enable_weather_effects") else pl.DataFrame()
    if weather_diagnostics.height:
        weather_diagnostics.write_parquet(qa_dir / "weather_sensitivity_kpis.parquet")
        weather_metrics = {row["Category"]: row for row in weather_diagnostics.iter_rows(named=True)}

        def weather_metric(category: str, column: str) -> float:
            value = weather_metrics.get(category, {}).get(column, 0.0)
            return float(value or 0.0)

        ride_weather_lift = weather_metric("Ride Hailing", "bad_weather_transaction_lift")
        food_weather_lift = weather_metric("Food Delivery", "bad_weather_transaction_lift")
        grocery_weather_gmv_lift = weather_metric("Grocery", "bad_weather_gmv_lift")
        grocery_weather_amount_lift = weather_metric("Grocery", "bad_weather_avg_amount_lift")
        ride_weather_completion_delta = weather_metric("Ride Hailing", "bad_weather_completion_delta")
        food_weather_completion_delta = weather_metric("Food Delivery", "bad_weather_completion_delta")
        digital_weather_lift = weather_metric("Digital Wallet", "bad_weather_transaction_lift")
    else:
        ride_weather_lift = 0.0
        food_weather_lift = 0.0
        grocery_weather_gmv_lift = 0.0
        grocery_weather_amount_lift = 0.0
        ride_weather_completion_delta = 0.0
        food_weather_completion_delta = 0.0
        digital_weather_lift = 0.0

    fraud_diagnostics = fraud_behavior_diagnostics(interactions) if metadata.get("enable_fraud_behavior") else {}
    if fraud_diagnostics:
        pl.DataFrame(
            {
                "metric": list(fraud_diagnostics.keys()),
                "value": list(fraud_diagnostics.values()),
            }
        ).write_csv(qa_dir / "fraud_behavior_diagnostics.csv")
    realism = realism_diagnostics(interactions, users, qa_dir)

    thresholds = config["validation"]
    is_full_size_validation = expected_row_count >= int(config["target_rows"])
    checks = [
        ("Exact target row count", row_count == expected_row_count, f"{row_count:,} / {expected_row_count:,}"),
        ("Non-partitioned interactions file exists", single_interactions is not None, str(single_interactions_path)),
        ("Non-partitioned row count matches partitions", single_row_count == row_count, f"{single_row_count:,} / {row_count:,}"),
        ("Non-partitioned schema matches partitions", single_schema == interaction_schema, "match" if single_schema == interaction_schema else "mismatch"),
        (
            "Non-partitioned monthly totals match partitions",
            max_single_month_row_diff == 0 and max_single_month_amount_diff <= 0.01,
            f"max row diff {max_single_month_row_diff:,}; max amount diff ${max_single_month_amount_diff:,.2f}",
        ),
        ("Unique Transaction_UUID", unique_transactions == row_count, f"{unique_transactions:,} unique"),
        ("All required columns present", not missing_columns, ", ".join(missing_columns) if missing_columns else "all present"),
        ("Zero nulls in required columns", total_nulls == 0, f"{total_nulls:,} nulls"),
        ("Full date coverage", not missing_dates, f"{len(missing_dates)} missing dates"),
        ("Category matches service category", category_mismatches == 0, f"{category_mismatches:,} mismatches"),
        ("User FK coverage", fk_user_missing == 0, f"{fk_user_missing:,} missing"),
        ("Service FK coverage", fk_service_missing == 0, f"{fk_service_missing:,} missing"),
        (
            "Annual active user rate",
            (not is_full_size_validation) or thresholds["active_user_rate_min"] <= active_user_rate <= thresholds["active_user_rate_max"],
            f"{active_user_rate:.2%}" if is_full_size_validation else f"{active_user_rate:.2%} (smoke run; full-scale threshold skipped)",
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
        (
            "Customer activity spread across lifecycle/membership",
            realism["min_customer_activity_spread"] >= thresholds["min_customer_activity_spread"],
            f"{realism['min_customer_activity_spread']:.2%}",
        ),
        (
            "Customer non-completion spread",
            realism["max_customer_non_completion_spread"] >= thresholds["min_customer_non_completion_spread"],
            f"{realism['max_customer_non_completion_spread']:.2%}",
        ),
        (
            "Market category share variation",
            realism["mean_category_share_std"] >= thresholds["min_mean_category_share_std"],
            f"mean std {realism['mean_category_share_std']:.2%}; min std {realism['min_category_share_std']:.2%}",
        ),
        (
            "Market/category amount variation",
            realism["mean_market_amount_std"] >= thresholds["min_mean_market_amount_std_usd"],
            f"${realism['mean_market_amount_std']:,.2f}",
        ),
        (
            "Market/category completion variation",
            realism["mean_market_completion_std"] >= thresholds["min_mean_market_completion_std"],
            f"{realism['mean_market_completion_std']:.2%}",
        ),
        (
            "Market monthly growth curves not parallel",
            realism["median_market_monthly_corr"] <= thresholds["max_median_market_monthly_corr"],
            f"median {realism['median_market_monthly_corr']:.4f}; max {realism['max_market_monthly_corr']:.4f}",
        ),
    ]
    if metadata.get("enable_weather_effects"):
        checks.extend(
            [
                (
                    "Ride Hailing bad-weather demand lift",
                    ride_weather_lift >= thresholds.get("min_ride_hailing_bad_weather_lift", 0.02),
                    f"{ride_weather_lift:.2%}",
                ),
                (
                    "Food Delivery bad-weather demand lift",
                    food_weather_lift >= thresholds.get("min_food_delivery_bad_weather_lift", 0.015),
                    f"{food_weather_lift:.2%}",
                ),
                (
                    "Digital Wallet less weather-sensitive than Ride Hailing",
                    digital_weather_lift < ride_weather_lift,
                    f"digital {digital_weather_lift:.2%}; ride {ride_weather_lift:.2%}",
                ),
                (
                    "Grocery bad-weather GMV lift",
                    grocery_weather_gmv_lift >= thresholds.get("min_grocery_bad_weather_gmv_lift", 0.015),
                    f"{grocery_weather_gmv_lift:.2%}",
                ),
                (
                    "Grocery bad-weather basket lift",
                    grocery_weather_amount_lift >= thresholds.get("min_grocery_bad_weather_avg_amount_lift", 0.01),
                    f"{grocery_weather_amount_lift:.2%}",
                ),
                (
                    "Ride Hailing bad-weather completion penalty",
                    ride_weather_completion_delta <= thresholds.get("max_ride_hailing_bad_weather_completion_delta", -0.002),
                    f"{ride_weather_completion_delta:.2%}",
                ),
                (
                    "Food Delivery bad-weather completion penalty",
                    food_weather_completion_delta <= thresholds.get("max_food_delivery_bad_weather_completion_delta", -0.002),
                    f"{food_weather_completion_delta:.2%}",
                ),
            ]
        )
    if metadata.get("enable_fraud_behavior"):
        checks.extend(
            [
                (
                    "Detectable high-velocity user-hour bursts",
                    fraud_diagnostics.get("burst_share", 0.0) >= thresholds.get("min_user_hour_burst_share", 0.004),
                    f"{fraud_diagnostics.get('burst_share', 0.0):.2%}",
                ),
                (
                    "High-velocity burst share remains moderate",
                    fraud_diagnostics.get("burst_share", 0.0) <= thresholds.get("max_user_hour_burst_share", 0.05),
                    f"{fraud_diagnostics.get('burst_share', 0.0):.2%}",
                ),
                (
                    "High-velocity user-hours have elevated non-completion",
                    fraud_diagnostics.get("burst_non_complete_rate", 0.0)
                    >= fraud_diagnostics.get("normal_user_hour_non_complete_rate", 0.0)
                    + thresholds.get("min_high_velocity_non_complete_lift", 0.04),
                    (
                        f"burst {fraud_diagnostics.get('burst_non_complete_rate', 0.0):.2%}; "
                        f"normal {fraud_diagnostics.get('normal_user_hour_non_complete_rate', 0.0):.2%}"
                    ),
                ),
                (
                    "High-amount transactions have elevated non-completion",
                    fraud_diagnostics.get("high_amount_non_complete_rate", 0.0)
                    >= fraud_diagnostics.get("non_complete_rate", 0.0) + thresholds.get("min_high_amount_non_complete_lift", 0.05),
                    (
                        f"high amount {fraud_diagnostics.get('high_amount_non_complete_rate', 0.0):.2%}; "
                        f"overall {fraud_diagnostics.get('non_complete_rate', 0.0):.2%}"
                    ),
                ),
                (
                    "Suspicious proxy share is detectable",
                    fraud_diagnostics.get("proxy_suspicious_share", 0.0) >= thresholds.get("min_proxy_suspicious_share", 0.003),
                    f"{fraud_diagnostics.get('proxy_suspicious_share', 0.0):.2%}",
                ),
                (
                    "Suspicious proxy share remains moderate",
                    fraud_diagnostics.get("proxy_suspicious_share", 0.0) <= thresholds.get("max_proxy_suspicious_share", 0.04),
                    f"{fraud_diagnostics.get('proxy_suspicious_share', 0.0):.2%}",
                ),
                (
                    "New/at-risk high-amount transactions have elevated non-completion",
                    fraud_diagnostics.get("new_at_risk_high_amount_non_complete_rate", 0.0)
                    >= fraud_diagnostics.get("other_high_amount_non_complete_rate", 0.0)
                    + thresholds.get("min_new_at_risk_high_amount_non_complete_lift", 0.03),
                    (
                        f"new/at-risk {fraud_diagnostics.get('new_at_risk_high_amount_non_complete_rate', 0.0):.2%}; "
                        f"other {fraud_diagnostics.get('other_high_amount_non_complete_rate', 0.0):.2%}"
                    ),
                ),
                (
                    "Suspicious proxy skews to web/lite platforms",
                    fraud_diagnostics.get("proxy_web_lite_share", 0.0)
                    >= fraud_diagnostics.get("baseline_web_lite_share", 0.0)
                    + thresholds.get("min_proxy_web_lite_lift", 0.06),
                    (
                        f"proxy {fraud_diagnostics.get('proxy_web_lite_share', 0.0):.2%}; "
                        f"baseline {fraud_diagnostics.get('baseline_web_lite_share', 0.0):.2%}"
                    ),
                ),
                (
                    "Suspicious proxy skews to promo referrals",
                    fraud_diagnostics.get("proxy_promo_referral_share", 0.0)
                    >= fraud_diagnostics.get("baseline_promo_referral_share", 0.0)
                    + thresholds.get("min_proxy_promo_referral_lift", 0.05),
                    (
                        f"proxy {fraud_diagnostics.get('proxy_promo_referral_share', 0.0):.2%}; "
                        f"baseline {fraud_diagnostics.get('baseline_promo_referral_share', 0.0):.2%}"
                    ),
                ),
                (
                    "Digital Wallet proxy signal exceeds other categories",
                    fraud_diagnostics.get("digital_wallet_proxy_share", 0.0)
                    >= fraud_diagnostics.get("other_category_proxy_share", 0.0)
                    + thresholds.get("min_digital_wallet_proxy_share_lift", 0.003),
                    (
                        f"digital {fraud_diagnostics.get('digital_wallet_proxy_share', 0.0):.2%}; "
                        f"other {fraud_diagnostics.get('other_category_proxy_share', 0.0):.2%}"
                    ),
                ),
                (
                    "E-Commerce proxy signal exceeds other categories",
                    fraud_diagnostics.get("ecommerce_proxy_share", 0.0)
                    >= fraud_diagnostics.get("other_category_proxy_share", 0.0)
                    + thresholds.get("min_ecommerce_proxy_share_lift", 0.002),
                    (
                        f"e-commerce {fraud_diagnostics.get('ecommerce_proxy_share', 0.0):.2%}; "
                        f"other {fraud_diagnostics.get('other_category_proxy_share', 0.0):.2%}"
                    ),
                ),
            ]
        )

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

## Realism diagnostics

{as_markdown_table(pl.DataFrame({"metric": list(realism.keys()), "value": list(realism.values())}), max_rows=30)}

## Weather sensitivity diagnostics

{as_markdown_table(weather_diagnostics, max_rows=20) if weather_diagnostics.height else "_Not enabled for this generation._"}

## Fraud-like behavior diagnostics

{as_markdown_table(pl.DataFrame({"metric": list(fraud_diagnostics.keys()), "value": list(fraud_diagnostics.values())}), max_rows=20) if fraud_diagnostics else "_Not enabled for this generation._"}

## Notes

- BigQuery should ingest corrected parquet files from `{input_dir}`, not `data/raw/`.
- BigQuery ingestion can use `{input_dir / "nova_interactions.parquet"}` when a non-partitioned interactions file is required.
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
