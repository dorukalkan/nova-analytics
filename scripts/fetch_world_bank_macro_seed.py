from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from external_geo_seed_utils import DEFAULT_SEEDS_DIR, MARKETS, WORLD_BANK_INDICATORS, fetch_json, fetched_at, write_csv


FIELDNAMES = [
    "country_iso3",
    "country_name",
    "indicator_code",
    "metric_name",
    "indicator_name",
    "indicator_year",
    "indicator_value",
    "source",
    "fetched_at_utc",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch World Bank macro indicator seed.")
    parser.add_argument("--seeds-dir", default=str(DEFAULT_SEEDS_DIR))
    parser.add_argument("--start-year", type=int, default=2020)
    parser.add_argument("--end-year", type=int, default=2024)
    return parser.parse_args()


def fetch_rows(start_year: int, end_year: int, now: str) -> list[dict[str, Any]]:
    countries = sorted({iso3 for *_rest, iso3 in MARKETS})
    rows: list[dict[str, Any]] = []
    for indicator_code, metric_name in WORLD_BANK_INDICATORS.items():
        for country_iso3 in countries:
            params = urlencode(
                {
                    "format": "json",
                    "date": f"{start_year}:{end_year}",
                    "per_page": 100,
                }
            )
            url = f"https://api.worldbank.org/v2/country/{country_iso3.lower()}/indicator/{indicator_code}?{params}"
            payload = fetch_json(url)
            if not isinstance(payload, list) or len(payload) < 2:
                raise RuntimeError(f"Unexpected World Bank response for {country_iso3} {indicator_code}")
            latest: dict[str, Any] | None = None
            for item in payload[1]:
                if item.get("value") is None:
                    continue
                year = int(item["date"])
                if latest is None or year > int(latest["indicator_year"]):
                    latest = {
                        "country_iso3": item.get("countryiso3code") or country_iso3,
                        "country_name": item["country"]["value"],
                        "indicator_code": indicator_code,
                        "metric_name": metric_name,
                        "indicator_name": item["indicator"]["value"],
                        "indicator_year": year,
                        "indicator_value": item["value"],
                        "source": "world_bank_api",
                        "fetched_at_utc": now,
                    }
            if latest is not None:
                rows.append(latest)
            print(f"fetched World Bank {indicator_code} for {country_iso3}", flush=True)
            time.sleep(0.1)
    return sorted(rows, key=lambda row: (row["country_iso3"], row["indicator_code"]))


def main() -> None:
    args = parse_args()
    output_path = Path(args.seeds_dir) / "ext_world_bank_indicators.csv"
    rows = fetch_rows(args.start_year, args.end_year, fetched_at())
    write_csv(output_path, FIELDNAMES, rows)
    print(f"wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
