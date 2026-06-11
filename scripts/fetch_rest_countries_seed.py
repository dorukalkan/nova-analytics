from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from external_geo_seed_utils import DEFAULT_SEEDS_DIR, MARKETS, fetch_json, fetched_at, load_env_file, write_csv


FIELDNAMES = [
    "country_iso3",
    "country_iso2",
    "country_name_common",
    "country_name_official",
    "region",
    "subregion",
    "capital",
    "currency_code",
    "currency_name",
    "currency_symbol",
    "population",
    "timezones",
    "source",
    "fetched_at_utc",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch country metadata seed from REST Countries.")
    parser.add_argument("--seeds-dir", default=str(DEFAULT_SEEDS_DIR))
    parser.add_argument("--env-file", default=".env")
    return parser.parse_args()


def fetch_rows(now: str) -> list[dict[str, Any]]:
    api_key = os.environ.get("REST_COUNTRIES_API_KEY")
    if not api_key:
        raise RuntimeError("REST_COUNTRIES_API_KEY is not set")

    fields = "names,codes,currencies,region,subregion,population,capitals,timezones"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload: list[dict[str, Any]] = []
    for offset in range(0, 300, 100):
        url = f"https://api.restcountries.com/countries/v5?{urlencode({'limit': 100, 'offset': offset, 'response_fields': fields})}"
        page = fetch_json(url, headers=headers)
        if isinstance(page, dict) and isinstance(page.get("data"), dict):
            data = page["data"]
            objects = data.get("objects")
            meta = data.get("meta") or {}
        else:
            objects = page
            meta = {}
        if not isinstance(objects, list):
            raise RuntimeError("Unexpected REST Countries response")
        payload.extend(objects)
        print(f"fetched REST Countries page offset {offset}", flush=True)
        if not meta.get("more", len(objects) == 100):
            break
        time.sleep(0.15)

    wanted = {iso3 for *_rest, iso3 in MARKETS}
    rows: list[dict[str, Any]] = []
    for item in payload:
        codes = item.get("codes") or {}
        iso3 = codes.get("alpha_3")
        if iso3 not in wanted:
            continue
        currencies = item.get("currencies") or []
        first_currency = currencies[0] if currencies else {}
        capitals = item.get("capitals") or []
        first_capital = capitals[0] if capitals else {}
        rows.append(
            {
                "country_iso3": iso3,
                "country_iso2": codes.get("alpha_2"),
                "country_name_common": (item.get("names") or {}).get("common"),
                "country_name_official": (item.get("names") or {}).get("official"),
                "region": item.get("region"),
                "subregion": item.get("subregion"),
                "capital": first_capital.get("name") if isinstance(first_capital, dict) else first_capital,
                "currency_code": first_currency.get("code") if isinstance(first_currency, dict) else None,
                "currency_name": first_currency.get("name") if isinstance(first_currency, dict) else None,
                "currency_symbol": first_currency.get("symbol") if isinstance(first_currency, dict) else None,
                "population": item.get("population"),
                "timezones": "|".join(item.get("timezones") or []),
                "source": "rest_countries_api",
                "fetched_at_utc": now,
            }
        )

    missing = wanted - {row["country_iso3"] for row in rows}
    if missing:
        raise RuntimeError(f"REST Countries response missing countries: {', '.join(sorted(missing))}")
    return sorted(rows, key=lambda row: row["country_iso3"])


def main() -> None:
    args = parse_args()
    load_env_file(Path(args.env_file))
    output_path = Path(args.seeds_dir) / "ext_country_metadata.csv"
    rows = fetch_rows(fetched_at())
    write_csv(output_path, FIELDNAMES, rows)
    print(f"wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
