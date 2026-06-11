from __future__ import annotations

import csv
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - fallback for partially bootstrapped envs
    load_dotenv = None


DEFAULT_SEEDS_DIR = Path("nova/seeds")

MARKETS = [
    (1, "Singapore", "Singapore", "SG", "SGP"),
    (2, "Jakarta", "Indonesia", "ID", "IDN"),
    (3, "Manila", "Philippines", "PH", "PHL"),
    (4, "Bangkok", "Thailand", "TH", "THA"),
    (5, "Ho Chi Minh City", "Vietnam", "VN", "VNM"),
    (6, "Istanbul", "Turkey", "TR", "TUR"),
    (7, "Dubai", "United Arab Emirates", "AE", "ARE"),
    (8, "Riyadh", "Saudi Arabia", "SA", "SAU"),
    (9, "London", "United Kingdom", "GB", "GBR"),
    (10, "New York", "United States", "US", "USA"),
    (11, "Mexico City", "Mexico", "MX", "MEX"),
    (12, "Sao Paulo", "Brazil", "BR", "BRA"),
    (13, "Mumbai", "India", "IN", "IND"),
    (14, "Bangalore", "India", "IN", "IND"),
    (15, "Tokyo", "Japan", "JP", "JPN"),
    (16, "Sydney", "Australia", "AU", "AUS"),
]

MARKET_COORDINATES = {
    1: (1.3521, 103.8198),
    2: (-6.2088, 106.8456),
    3: (14.5995, 120.9842),
    4: (13.7563, 100.5018),
    5: (10.8231, 106.6297),
    6: (41.0082, 28.9784),
    7: (25.2048, 55.2708),
    8: (24.7136, 46.6753),
    9: (51.5072, -0.1276),
    10: (40.7128, -74.0060),
    11: (19.4326, -99.1332),
    12: (-23.5558, -46.6396),
    13: (19.0760, 72.8777),
    14: (12.9716, 77.5946),
    15: (35.6762, 139.6503),
    16: (-33.8688, 151.2093),
}

WORLD_BANK_INDICATORS = {
    "SP.POP.TOTL": "population_total",
    "NY.GDP.PCAP.CD": "gdp_per_capita_current_usd",
    "SP.URB.TOTL.IN.ZS": "urban_population_pct",
    "IT.NET.USER.ZS": "internet_users_pct",
    "IT.CEL.SETS.P2": "mobile_subscriptions_per_100_people",
}


def fetched_at() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_env_file(path: Path) -> None:
    if load_dotenv is not None:
        load_dotenv(path)
        return
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def fetch_json(url: str, headers: dict[str, str] | None = None, timeout: int = 60) -> Any:
    request_headers = {"User-Agent": "nova-analytics-seed-fetcher/1.0"}
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:500]}") from exc
    except URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
