from __future__ import annotations

import argparse
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch all external geography seeds.")
    parser.add_argument("--seeds-dir", default="nova/seeds")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--world-bank-start-year", type=int, default=2020)
    parser.add_argument("--skip-rest-countries", action="store_true")
    return parser.parse_args()


def run(command: list[str]) -> None:
    print("running " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> None:
    args = parse_args()
    python = sys.executable
    run([python, "scripts/fetch_market_country_lookup_seed.py", "--seeds-dir", args.seeds_dir])
    run([python, "scripts/fetch_open_meteo_weather_seed.py", "--seeds-dir", args.seeds_dir, "--year", str(args.year)])
    run(
        [
            python,
            "scripts/fetch_world_bank_macro_seed.py",
            "--seeds-dir",
            args.seeds_dir,
            "--start-year",
            str(args.world_bank_start_year),
            "--end-year",
            str(args.year),
        ]
    )
    if not args.skip_rest_countries:
        run([python, "scripts/fetch_rest_countries_seed.py", "--seeds-dir", args.seeds_dir, "--env-file", args.env_file])


if __name__ == "__main__":
    main()
