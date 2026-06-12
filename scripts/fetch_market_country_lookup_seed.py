from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from external_geo_seed_utils import DEFAULT_SEEDS_DIR, MARKETS, fetched_at, write_csv


FIELDNAMES = [
    "market_id",
    "market_name",
    "country_name",
    "country_iso2",
    "country_iso3",
    "world_bank_country_code",
    "source",
    "fetched_at_utc",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write the reviewed Nova market-to-country lookup seed.")
    parser.add_argument("--seeds-dir", default=str(DEFAULT_SEEDS_DIR))
    return parser.parse_args()


def build_rows(now: str) -> list[dict[str, Any]]:
    rows = []
    for market_id, market_name, country_name, iso2, iso3 in MARKETS:
        rows.append(
            {
                "market_id": market_id,
                "market_name": market_name,
                "country_name": country_name,
                "country_iso2": iso2,
                "country_iso3": iso3,
                "world_bank_country_code": iso3.lower(),
                "source": "manual_reviewed_lookup",
                "fetched_at_utc": now,
            }
        )
    return rows


def main() -> None:
    output_path = Path(parse_args().seeds_dir) / "market_country_lookup.csv"
    rows = build_rows(fetched_at())
    write_csv(output_path, FIELDNAMES, rows)
    print(f"wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
