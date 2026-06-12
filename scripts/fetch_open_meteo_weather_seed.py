from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from external_geo_seed_utils import DEFAULT_SEEDS_DIR, MARKET_COORDINATES, MARKETS, fetch_json, fetched_at, write_csv


FIELDNAMES = [
    "market_id",
    "market_name",
    "weather_date",
    "weather_code",
    "temperature_2m_mean_c",
    "temperature_2m_max_c",
    "temperature_2m_min_c",
    "apparent_temperature_mean_c",
    "precipitation_sum_mm",
    "rain_sum_mm",
    "precipitation_hours",
    "wind_speed_10m_max_kmh",
    "is_rain_day",
    "source",
    "fetched_at_utc",
]

DAILY_VARIABLES = [
    "weather_code",
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_mean",
    "precipitation_sum",
    "rain_sum",
    "precipitation_hours",
    "wind_speed_10m_max",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch daily market weather seed from Open-Meteo.")
    parser.add_argument("--seeds-dir", default=str(DEFAULT_SEEDS_DIR))
    parser.add_argument("--year", type=int, default=2024)
    return parser.parse_args()


def fetch_rows(year: int, now: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for market_id, market_name, *_ in MARKETS:
        latitude, longitude = MARKET_COORDINATES[market_id]
        params = urlencode(
            {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": f"{year}-01-01",
                "end_date": f"{year}-12-31",
                "daily": ",".join(DAILY_VARIABLES),
                "timezone": "auto",
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "precipitation_unit": "mm",
            }
        )
        payload = fetch_json(f"https://archive-api.open-meteo.com/v1/archive?{params}")
        daily = payload["daily"]
        dates = daily["time"]
        for idx, weather_date in enumerate(dates):
            rain_sum = daily.get("rain_sum", [None] * len(dates))[idx]
            precipitation_sum = daily.get("precipitation_sum", [None] * len(dates))[idx]
            rows.append(
                {
                    "market_id": market_id,
                    "market_name": market_name,
                    "weather_date": weather_date,
                    "weather_code": daily.get("weather_code", [None] * len(dates))[idx],
                    "temperature_2m_mean_c": daily.get("temperature_2m_mean", [None] * len(dates))[idx],
                    "temperature_2m_max_c": daily.get("temperature_2m_max", [None] * len(dates))[idx],
                    "temperature_2m_min_c": daily.get("temperature_2m_min", [None] * len(dates))[idx],
                    "apparent_temperature_mean_c": daily.get("apparent_temperature_mean", [None] * len(dates))[idx],
                    "precipitation_sum_mm": precipitation_sum,
                    "rain_sum_mm": rain_sum,
                    "precipitation_hours": daily.get("precipitation_hours", [None] * len(dates))[idx],
                    "wind_speed_10m_max_kmh": daily.get("wind_speed_10m_max", [None] * len(dates))[idx],
                    "is_rain_day": bool((rain_sum or 0) > 0 or (precipitation_sum or 0) > 0),
                    "source": "open_meteo_historical_weather_api",
                    "fetched_at_utc": now,
                }
            )
        print(f"fetched Open-Meteo weather for {market_name}", flush=True)
        time.sleep(0.15)
    return rows


def main() -> None:
    args = parse_args()
    output_path = Path(args.seeds_dir) / "ext_weather_daily.csv"
    rows = fetch_rows(args.year, fetched_at())
    write_csv(output_path, FIELDNAMES, rows)
    print(f"wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
