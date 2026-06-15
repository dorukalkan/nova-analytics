from __future__ import annotations

import argparse
import calendar
import json
import shutil
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl
import yaml


CATEGORIES = ["Food Delivery", "Ride Hailing", "E-Commerce", "Grocery", "Digital Wallet"]
REFERRAL_SOURCES = ["Organic Search", "Friend Referral", "Email Promo", "Social Ad", "Push Notification"]

TROPICAL_MONSOON_MARKETS = {1, 2, 3, 4, 5, 13}
ARID_HEAT_MARKETS = {7, 8}
TEMPERATE_SEASONAL_MARKETS = {6, 9, 10, 11, 12, 14, 15, 16}

MARKET_CATEGORY_AFFINITY = {
    1: {"Food Delivery": 1.08, "Ride Hailing": 0.92, "E-Commerce": 1.20, "Grocery": 1.18, "Digital Wallet": 1.05},
    2: {"Food Delivery": 1.18, "Ride Hailing": 1.18, "E-Commerce": 0.88, "Grocery": 0.92, "Digital Wallet": 1.22},
    3: {"Food Delivery": 1.22, "Ride Hailing": 1.05, "E-Commerce": 0.94, "Grocery": 0.92, "Digital Wallet": 1.14},
    4: {"Food Delivery": 1.24, "Ride Hailing": 1.08, "E-Commerce": 0.92, "Grocery": 0.96, "Digital Wallet": 1.02},
    5: {"Food Delivery": 1.28, "Ride Hailing": 1.12, "E-Commerce": 0.86, "Grocery": 0.90, "Digital Wallet": 1.16},
    6: {"Food Delivery": 1.12, "Ride Hailing": 1.08, "E-Commerce": 1.02, "Grocery": 1.10, "Digital Wallet": 0.86},
    7: {"Food Delivery": 0.96, "Ride Hailing": 1.18, "E-Commerce": 1.18, "Grocery": 1.12, "Digital Wallet": 0.88},
    8: {"Food Delivery": 0.92, "Ride Hailing": 1.22, "E-Commerce": 1.12, "Grocery": 1.08, "Digital Wallet": 0.92},
    9: {"Food Delivery": 0.90, "Ride Hailing": 0.92, "E-Commerce": 1.28, "Grocery": 1.08, "Digital Wallet": 0.90},
    10: {"Food Delivery": 0.96, "Ride Hailing": 1.02, "E-Commerce": 1.30, "Grocery": 0.98, "Digital Wallet": 0.88},
    11: {"Food Delivery": 1.10, "Ride Hailing": 1.16, "E-Commerce": 0.96, "Grocery": 0.98, "Digital Wallet": 1.10},
    12: {"Food Delivery": 1.08, "Ride Hailing": 1.18, "E-Commerce": 1.00, "Grocery": 1.00, "Digital Wallet": 0.98},
    13: {"Food Delivery": 1.08, "Ride Hailing": 1.20, "E-Commerce": 0.96, "Grocery": 0.90, "Digital Wallet": 1.34},
    14: {"Food Delivery": 0.98, "Ride Hailing": 1.16, "E-Commerce": 1.12, "Grocery": 0.94, "Digital Wallet": 1.26},
    15: {"Food Delivery": 0.86, "Ride Hailing": 0.92, "E-Commerce": 1.32, "Grocery": 1.16, "Digital Wallet": 0.92},
    16: {"Food Delivery": 0.92, "Ride Hailing": 0.96, "E-Commerce": 1.20, "Grocery": 1.20, "Digital Wallet": 0.88},
}

MARKET_AMOUNT_MULTIPLIER = np.array(
    [1.00, 1.10, 0.82, 0.86, 0.88, 0.78, 0.86, 1.22, 1.12, 1.42, 1.38, 0.74, 0.72, 0.60, 0.66, 1.18, 1.28],
    dtype=np.float64,
)

MARKET_COMPLETION_ADJUSTMENT = np.array(
    [0.0, 0.006, -0.010, -0.008, -0.006, -0.004, -0.003, 0.004, -0.002, 0.008, 0.010, -0.012, -0.009, -0.014, -0.011, 0.007, 0.006],
    dtype=np.float64,
)


@dataclass(frozen=True)
class Paths:
    raw_dir: Path
    output_dir: Path


@dataclass(frozen=True)
class WeatherEffects:
    enabled: bool
    start_date: np.datetime64
    demand_multiplier: np.ndarray
    amount_multiplier: np.ndarray
    completion_adjustment: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate corrected Nova parquet tables before BigQuery ingestion.")
    parser.add_argument("--config", default="config/nova_correction.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--target-rows", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--enable-weather-effects", action="store_true")
    parser.add_argument("--enable-fraud-behavior", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def month_starts(start: str, end: str) -> list[date]:
    start_dt = datetime.strptime(start, "%Y-%m-%d").date().replace(day=1)
    end_dt = datetime.strptime(end, "%Y-%m-%d").date().replace(day=1)
    months: list[date] = []
    current = start_dt
    while current <= end_dt:
        months.append(current)
        year = current.year + (current.month // 12)
        month = 1 if current.month == 12 else current.month + 1
        current = date(year, month, 1)
    return months


def allocate_counts(total: int, shares_by_month: dict[str, float], months: list[date]) -> dict[str, int]:
    shares = np.array([float(shares_by_month[m.strftime("%Y-%m")]) for m in months], dtype=np.float64)
    shares = shares / shares.sum()
    raw_counts = shares * total
    counts = np.floor(raw_counts).astype(np.int64)
    remainder = total - int(counts.sum())
    if remainder:
        order = np.argsort(raw_counts - counts)[::-1]
        counts[order[:remainder]] += 1
    return {month.strftime("%Y-%m"): int(count) for month, count in zip(months, counts)}


def weighted_choice(rng: np.random.Generator, values: np.ndarray, probabilities: np.ndarray, size: int) -> np.ndarray:
    probabilities = probabilities.astype(np.float64)
    probabilities = probabilities / probabilities.sum()
    return rng.choice(values, size=size, replace=True, p=probabilities)


def normalize(values: np.ndarray) -> np.ndarray:
    values = values.astype(np.float64)
    total = values.sum()
    if total <= 0:
        return np.full(len(values), 1.0 / len(values))
    return values / total


def category_index(values: np.ndarray) -> np.ndarray:
    index = np.full(len(values), CATEGORIES.index("Digital Wallet"), dtype=np.int16)
    for position, category in enumerate(CATEGORIES):
        index[values == category] = position
    return index


def category_affinity_vector(market_id: int) -> np.ndarray:
    affinity = MARKET_CATEGORY_AFFINITY[int(market_id)]
    return np.array([affinity[category] for category in CATEGORIES], dtype=np.float64)


def market_category_probs(config: dict, month_key: str, market_id: int) -> np.ndarray:
    return normalize(category_probs_for_month(config, month_key) * category_affinity_vector(market_id))


def market_month_multiplier(month: date, market_id: int) -> float:
    month_number = month.month
    region_like = {
        "sea": {1, 2, 3, 4, 5},
        "emea": {6, 7, 8},
        "west": {9, 10, 16},
        "latam": {11, 12},
        "india": {13, 14},
        "east_asia": {15},
    }
    multiplier = 1.0
    if market_id in region_like["sea"] and month_number in (6, 7, 8, 9):
        multiplier *= 1.03 + 0.01 * ((market_id % 3) - 1)
    if market_id in region_like["emea"] and month_number in (7, 8):
        multiplier *= 0.94 if market_id in (7, 8) else 1.02
    if market_id in region_like["west"] and month_number in (11, 12):
        multiplier *= 1.06 if market_id in (9, 10) else 1.03
    if market_id in region_like["latam"] and month_number in (5, 6, 7):
        multiplier *= 1.04
    if market_id in region_like["india"] and month_number in (9, 10, 11):
        multiplier *= 1.05
    if market_id in region_like["east_asia"] and month_number in (3, 4, 12):
        multiplier *= 1.04
    multiplier *= 1.0 + ((market_id % 5) - 2) * 0.006
    return multiplier


def user_activity_multiplier(segment: np.ndarray, lifecycle: np.ndarray, membership: np.ndarray) -> np.ndarray:
    segment_multiplier = np.select(
        [
            segment == "New",
            segment == "Casual",
            segment == "Regular",
            segment == "Power",
        ],
        [0.80, 0.42, 1.35, 5.70],
        default=0.04,
    ).astype(np.float64)
    lifecycle_multiplier = np.select(
        [
            lifecycle == "High Value",
            lifecycle == "Retained",
            lifecycle == "At Risk",
            lifecycle == "New Active",
            lifecycle == "Inactive",
        ],
        [1.18, 1.00, 0.68, 0.82, 0.05],
        default=1.0,
    ).astype(np.float64)
    membership_multiplier = np.select(
        [
            membership == "Platinum",
            membership == "Gold",
            membership == "Standard",
        ],
        [1.35, 1.16, 1.00],
        default=1.0,
    ).astype(np.float64)
    return segment_multiplier * lifecycle_multiplier * membership_multiplier


def user_amount_multiplier(membership: np.ndarray, lifecycle: np.ndarray) -> np.ndarray:
    membership_multiplier = np.select(
        [
            membership == "Platinum",
            membership == "Gold",
            membership == "Standard",
        ],
        [1.18, 1.08, 1.00],
        default=1.0,
    ).astype(np.float64)
    lifecycle_multiplier = np.select(
        [
            lifecycle == "High Value",
            lifecycle == "At Risk",
            lifecycle == "New Active",
            lifecycle == "Inactive",
        ],
        [1.10, 0.92, 0.96, 0.86],
        default=1.0,
    ).astype(np.float64)
    return membership_multiplier * lifecycle_multiplier


def user_completion_adjustment(membership: np.ndarray, lifecycle: np.ndarray) -> np.ndarray:
    membership_adjustment = np.select(
        [
            membership == "Platinum",
            membership == "Gold",
        ],
        [0.010, 0.005],
        default=0.0,
    ).astype(np.float64)
    lifecycle_adjustment = np.select(
        [
            lifecycle == "High Value",
            lifecycle == "At Risk",
            lifecycle == "New Active",
            lifecycle == "Inactive",
        ],
        [0.004, -0.018, -0.008, -0.025],
        default=0.0,
    ).astype(np.float64)
    return membership_adjustment + lifecycle_adjustment


def create_markets(config: dict) -> pl.DataFrame:
    markets = config["markets"]
    return pl.DataFrame(
        {
            "Market_ID": [market["id"] for market in markets],
            "Market_Name": [market["name"] for market in markets],
            "Region": [market["region"] for market in markets],
            "Latitude": [market["lat"] for market in markets],
            "Longitude": [market["long"] for market in markets],
            "Market_Weight": [market["weight"] for market in markets],
            "Growth_Multiplier": [market["growth"] for market in markets],
            "IOS_Share": [market["ios_share"] for market in markets],
        }
    )


def random_dates(
    rng: np.random.Generator,
    start: date,
    end: date,
    size: int,
    favor_recent: bool = False,
) -> np.ndarray:
    n_days = (end - start).days + 1
    day_offsets = np.arange(n_days)
    if favor_recent:
        weights = np.linspace(0.7, 1.4, n_days)
        chosen = rng.choice(day_offsets, size=size, replace=True, p=normalize(weights))
    else:
        chosen = rng.integers(0, n_days, size=size)
    return np.array([start + timedelta(days=int(offset)) for offset in chosen], dtype="datetime64[D]")


def generate_users(raw_users: pl.DataFrame, markets: pl.DataFrame, config: dict, rng: np.random.Generator) -> pl.DataFrame:
    user_ids = raw_users.sort("User_ID")["User_ID"].to_numpy()
    n_users = len(user_ids)

    market_ids = markets["Market_ID"].to_numpy()
    market_weights = normalize(markets["Market_Weight"].to_numpy())
    user_market_ids = weighted_choice(rng, market_ids, market_weights, n_users)

    market_lookup = markets.sort("Market_ID")
    market_names = market_lookup["Market_Name"].to_numpy()
    regions = market_lookup["Region"].to_numpy()
    ios_shares = market_lookup["IOS_Share"].to_numpy()
    market_index = user_market_ids - 1

    primary_device = np.where(rng.random(n_users) < ios_shares[market_index], "iOS", "Android")

    segment_names = np.array(list(config["user_segments"].keys()), dtype=object)
    segment_probs = normalize(np.array(list(config["user_segments"].values()), dtype=np.float64))
    user_segment = weighted_choice(rng, segment_names, segment_probs, n_users)

    join_dates = np.empty(n_users, dtype="datetime64[D]")
    new_mask = user_segment == "New"
    join_dates[new_mask] = random_dates(rng, date(2024, 1, 1), date(2024, 12, 1), int(new_mask.sum()), favor_recent=True)
    old_mask = ~new_mask
    join_dates[old_mask] = random_dates(rng, date(2022, 1, 1), date(2023, 12, 31), int(old_mask.sum()))

    membership = np.full(n_users, "Standard", dtype=object)
    for segment, probs in {
        "Dormant": [0.96, 0.04, 0.00],
        "Casual": [0.90, 0.09, 0.01],
        "Regular": [0.58, 0.34, 0.08],
        "Power": [0.22, 0.46, 0.32],
        "New": [0.93, 0.07, 0.00],
    }.items():
        mask = user_segment == segment
        if mask.any():
            membership[mask] = weighted_choice(
                rng,
                np.array(["Standard", "Gold", "Platinum"], dtype=object),
                np.array(probs, dtype=np.float64),
                int(mask.sum()),
            )

    acquisition_probs = np.array([0.32, 0.20, 0.16, 0.22, 0.10])
    acquisition = weighted_choice(rng, np.array(REFERRAL_SOURCES, dtype=object), acquisition_probs, n_users)
    acquisition[user_segment == "New"] = weighted_choice(
        rng,
        np.array(["Organic Search", "Friend Referral", "Email Promo", "Social Ad"], dtype=object),
        np.array([0.34, 0.24, 0.18, 0.24]),
        int((user_segment == "New").sum()),
    )

    lifecycle = np.full(n_users, "Retained", dtype=object)
    lifecycle[user_segment == "Dormant"] = "Inactive"
    lifecycle[user_segment == "New"] = "New Active"
    lifecycle[user_segment == "Power"] = "High Value"
    at_risk_mask = ((user_segment == "Casual") & (rng.random(n_users) < 0.32)) | (
        (user_segment == "Regular") & (membership == "Standard") & (rng.random(n_users) < 0.07)
    )
    lifecycle[at_risk_mask] = "At Risk"

    return pl.DataFrame(
        {
            "User_ID": user_ids,
            "Join_Date": join_dates,
            "Membership_Tier": membership,
            "Primary_Device": primary_device,
            "Market_ID": user_market_ids,
            "Market_Name": market_names[market_index],
            "Region": regions[market_index],
            "Acquisition_Source": acquisition,
            "User_Segment": user_segment,
            "Lifecycle_Segment": lifecycle,
        }
    )


def generate_services(raw_services: pl.DataFrame, markets: pl.DataFrame, config: dict, rng: np.random.Generator) -> pl.DataFrame:
    raw_services = raw_services.sort("Service_ID")
    service_ids = raw_services["Service_ID"].to_numpy()
    merchant_names = raw_services["Merchant_Name"].to_numpy()
    n_services = len(service_ids)

    market_ids = markets["Market_ID"].to_numpy()
    market_weights = normalize(markets["Market_Weight"].to_numpy())
    service_market_ids = weighted_choice(rng, market_ids, market_weights, n_services)
    market_lookup = markets.sort("Market_ID")
    market_names = market_lookup["Market_Name"].to_numpy()
    regions = market_lookup["Region"].to_numpy()
    market_index = service_market_ids - 1

    categories = np.empty(n_services, dtype=object)
    base_category_weights = np.array([config["categories"][category]["base_share"] for category in CATEGORIES], dtype=np.float64)
    for market_id in market_ids:
        mask = service_market_ids == market_id
        if mask.any():
            category_weights = normalize(base_category_weights * category_affinity_vector(int(market_id)))
            categories[mask] = weighted_choice(rng, np.array(CATEGORIES, dtype=object), category_weights, int(mask.sum()))

    tier_names = np.array(list(config["service_tiers"].keys()), dtype=object)
    tier_probs = normalize(np.array(list(config["service_tiers"].values()), dtype=np.float64))
    service_tier = weighted_choice(rng, tier_names, tier_probs, n_services)

    popularity = np.empty(n_services, dtype=np.float64)
    popularity[service_tier == "Head"] = rng.lognormal(mean=3.65, sigma=0.48, size=int((service_tier == "Head").sum()))
    popularity[service_tier == "Mid"] = rng.lognormal(mean=1.45, sigma=0.55, size=int((service_tier == "Mid").sum()))
    popularity[service_tier == "Long Tail"] = rng.lognormal(mean=0.10, sigma=0.60, size=int((service_tier == "Long Tail").sum()))

    rating = 3.0 + (rng.beta(5.5, 2.2, size=n_services) * 2.0)
    rating += np.where(service_tier == "Head", 0.10, 0.0)
    rating -= np.where(service_tier == "Long Tail", 0.05, 0.0)
    rating = np.round(np.clip(rating, 3.0, 5.0), 1)

    return pl.DataFrame(
        {
            "Service_ID": service_ids,
            "Merchant_Name": merchant_names,
            "Category": categories,
            "Rating": rating,
            "Market_ID": service_market_ids,
            "Market_Name": market_names[market_index],
            "Region": regions[market_index],
            "Service_Tier": service_tier,
            "Popularity_Score": popularity,
        }
    )


def build_lookup_arrays(users: pl.DataFrame, services: pl.DataFrame, markets: pl.DataFrame) -> dict:
    users_sorted = users.sort("User_ID")
    services_sorted = services.sort("Service_ID")
    markets_sorted = markets.sort("Market_ID")

    return {
        "user_ids": users_sorted["User_ID"].to_numpy(),
        "user_join_dates": users_sorted["Join_Date"].to_numpy().astype("datetime64[D]"),
        "user_market_ids": users_sorted["Market_ID"].to_numpy(),
        "user_segments": users_sorted["User_Segment"].to_numpy(),
        "lifecycle_segments": users_sorted["Lifecycle_Segment"].to_numpy(),
        "membership_tiers": users_sorted["Membership_Tier"].to_numpy(),
        "primary_devices": users_sorted["Primary_Device"].to_numpy(),
        "acquisition_sources": users_sorted["Acquisition_Source"].to_numpy(),
        "service_ids": services_sorted["Service_ID"].to_numpy(),
        "service_market_ids": services_sorted["Market_ID"].to_numpy(),
        "service_categories": services_sorted["Category"].to_numpy(),
        "service_ratings": services_sorted["Rating"].to_numpy(),
        "service_tiers": services_sorted["Service_Tier"].to_numpy(),
        "service_popularity": services_sorted["Popularity_Score"].to_numpy(),
        "market_names": markets_sorted["Market_Name"].to_numpy(),
        "market_regions": markets_sorted["Region"].to_numpy(),
        "market_lats": markets_sorted["Latitude"].to_numpy(),
        "market_longs": markets_sorted["Longitude"].to_numpy(),
        "market_weights": normalize(markets_sorted["Market_Weight"].to_numpy() * markets_sorted["Growth_Multiplier"].to_numpy()),
    }


def user_weight(segment: np.ndarray, membership: np.ndarray | None = None) -> np.ndarray:
    if membership is None:
        membership = np.full(len(segment), "Standard", dtype=object)
    return user_activity_multiplier(segment, np.full(len(segment), "Retained", dtype=object), membership)


def precompute_user_pools(lookup: dict, months: list[date]) -> dict[tuple[str, int], tuple[np.ndarray, np.ndarray]]:
    pools: dict[tuple[str, int], tuple[np.ndarray, np.ndarray]] = {}
    user_ids = lookup["user_ids"]
    join_dates = lookup["user_join_dates"]
    market_ids = lookup["user_market_ids"]
    segments = lookup["user_segments"]
    lifecycle = lookup["lifecycle_segments"]
    membership = lookup["membership_tiers"]
    weights = user_activity_multiplier(segments, lifecycle, membership)
    for month in months:
        month_end = np.datetime64(date(month.year, month.month, calendar.monthrange(month.year, month.month)[1]))
        for market_id in range(1, 17):
            mask = (market_ids == market_id) & (join_dates <= month_end) & (weights > 0)
            candidates = user_ids[mask]
            candidate_weights = normalize(weights[mask])
            pools[(month.strftime("%Y-%m"), market_id)] = (candidates, candidate_weights)
    return pools


def precompute_service_pools(lookup: dict) -> dict[tuple[int, str], tuple[np.ndarray, np.ndarray]]:
    pools: dict[tuple[int, str], tuple[np.ndarray, np.ndarray]] = {}
    service_ids = lookup["service_ids"]
    market_ids = lookup["service_market_ids"]
    categories = lookup["service_categories"]
    popularity = lookup["service_popularity"]
    for market_id in range(1, 17):
        for category in CATEGORIES:
            mask = (market_ids == market_id) & (categories == category)
            if not mask.any():
                mask = categories == category
            pools[(market_id, category)] = (service_ids[mask], normalize(popularity[mask]))
    return pools


def category_probs_for_month(config: dict, month_key: str) -> np.ndarray:
    weights = np.array([config["categories"][category]["base_share"] for category in CATEGORIES], dtype=np.float64)
    month = int(month_key[-2:])
    if month in (11, 12):
        weights[CATEGORIES.index("E-Commerce")] *= 1.45 if month == 11 else 1.35
        weights[CATEGORIES.index("Digital Wallet")] *= 1.18
    if month in (6, 7, 8):
        weights[CATEGORIES.index("Ride Hailing")] *= 1.08
        weights[CATEGORIES.index("Food Delivery")] *= 1.05
    return normalize(weights)


def day_probabilities(month: date, category: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n_days = calendar.monthrange(month.year, month.month)[1]
    dates = np.array([date(month.year, month.month, day) for day in range(1, n_days + 1)], dtype="datetime64[D]")
    weights = np.ones(n_days, dtype=np.float64)
    weekdays = np.array([datetime(month.year, month.month, day).weekday() for day in range(1, n_days + 1)])

    if category in {"Food Delivery", "Grocery", "E-Commerce"}:
        weights[weekdays >= 5] *= 1.22
    if category == "Ride Hailing":
        weights[weekdays < 5] *= 1.15
        weights[weekdays >= 5] *= 1.08
    if category == "Digital Wallet":
        for day in (1, 15, n_days):
            weights[day - 1] *= 1.35
    if month.month in (11, 12) and category == "E-Commerce":
        weights *= np.linspace(1.0, 1.45, n_days)
    return dates, weekdays, normalize(weights)


def empty_weather_effects(config: dict) -> WeatherEffects:
    start = np.datetime64(datetime.strptime(config["dates"]["start"], "%Y-%m-%d").date())
    end = np.datetime64(datetime.strptime(config["dates"]["end"], "%Y-%m-%d").date())
    n_days = int((end - start).astype("timedelta64[D]").astype(int)) + 1
    shape = (17, n_days, len(CATEGORIES))
    return WeatherEffects(
        enabled=False,
        start_date=start,
        demand_multiplier=np.ones(shape, dtype=np.float64),
        amount_multiplier=np.ones(shape, dtype=np.float64),
        completion_adjustment=np.zeros(shape, dtype=np.float64),
    )


def load_weather_effects(config: dict, enabled: bool) -> WeatherEffects:
    effects = empty_weather_effects(config)
    if not enabled:
        return effects

    weather_path = Path(config["paths"].get("weather_seed", "nova/seeds/ext_weather_daily.csv"))
    if not weather_path.exists():
        raise SystemExit(f"Weather effects requested, but {weather_path} does not exist.")

    weather = (
        pl.read_csv(weather_path, try_parse_dates=True)
        .with_columns(pl.col("weather_date").dt.strftime("%Y-%m").alias("month_key"))
        .with_columns(
            [
                pl.col("precipitation_sum_mm").fill_null(0.0),
                pl.col("wind_speed_10m_max_kmh").fill_null(0.0),
                pl.col("temperature_2m_mean_c").fill_null(strategy="mean"),
            ]
        )
    )
    monthly = weather.group_by(["market_id", "month_key"]).agg(
        pl.col("temperature_2m_mean_c").mean().alias("month_temp_mean"),
        pl.col("temperature_2m_mean_c").quantile(0.10).alias("month_temp_p10"),
        pl.col("temperature_2m_mean_c").quantile(0.90).alias("month_temp_p90"),
    )
    market_quantiles = weather.group_by("market_id").agg(
        pl.col("precipitation_sum_mm").quantile(0.70).alias("market_precip_p70"),
        pl.col("precipitation_sum_mm").quantile(0.90).alias("market_precip_p90"),
        pl.col("wind_speed_10m_max_kmh").quantile(0.90).alias("market_wind_p90"),
    )
    enriched = (
        weather.join(monthly, on=["market_id", "month_key"], how="left")
        .join(market_quantiles, on="market_id", how="left")
        .with_columns(
            [
                (
                    pl.col("is_rain_day")
                    & (pl.col("precipitation_sum_mm") < pl.max_horizontal(pl.col("market_precip_p70"), pl.lit(3.0)))
                ).alias("is_light_rain"),
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
    )

    demand = effects.demand_multiplier.copy()
    amount = effects.amount_multiplier.copy()
    completion = effects.completion_adjustment.copy()
    start = effects.start_date

    for row in enriched.iter_rows(named=True):
        market_id = int(row["market_id"])
        day_index = int((np.datetime64(row["weather_date"]) - start).astype("timedelta64[D]").astype(int))
        if day_index < 0 or day_index >= demand.shape[1]:
            continue

        is_rain = bool(row["is_rain_day"])
        is_light_rain = bool(row["is_light_rain"])
        is_moderate_rain = bool(row["is_moderate_rain"])
        is_heavy_rain = bool(row["is_heavy_rain"])
        is_extreme_heat = bool(row["is_extreme_heat"])
        is_extreme_cold = bool(row["is_extreme_cold"])
        is_high_wind = bool(row["is_high_wind"])
        is_storm_like = is_heavy_rain and is_high_wind
        is_bad_weather = is_heavy_rain or is_extreme_heat or is_extreme_cold or is_high_wind

        if market_id in TROPICAL_MONSOON_MARKETS:
            rain_sensitivity = 0.78 if not is_heavy_rain else 1.05
            heat_sensitivity = 0.92
            cold_sensitivity = 0.55
            wind_sensitivity = 0.95
        elif market_id in ARID_HEAT_MARKETS:
            rain_sensitivity = 1.18
            heat_sensitivity = 1.35
            cold_sensitivity = 0.45
            wind_sensitivity = 1.05
        elif market_id in TEMPERATE_SEASONAL_MARKETS:
            rain_sensitivity = 1.04
            heat_sensitivity = 1.00
            cold_sensitivity = 1.18
            wind_sensitivity = 1.10
        else:
            rain_sensitivity = 1.0
            heat_sensitivity = 1.0
            cold_sensitivity = 1.0
            wind_sensitivity = 1.0

        for cat_pos, category in enumerate(CATEGORIES):
            demand_factor = 1.0
            amount_factor = 1.0
            completion_delta = 0.0

            if category == "Ride Hailing":
                demand_factor += 0.04 * rain_sensitivity if is_light_rain else 0.0
                demand_factor += 0.11 * rain_sensitivity if is_moderate_rain else 0.0
                demand_factor += 0.22 * rain_sensitivity if is_heavy_rain else 0.0
                demand_factor += 0.07 * heat_sensitivity if is_extreme_heat else 0.0
                demand_factor += 0.06 * cold_sensitivity if is_extreme_cold else 0.0
                completion_delta -= 0.014 if is_bad_weather else 0.0
                completion_delta -= 0.018 * wind_sensitivity if is_high_wind else 0.0
                completion_delta -= 0.008 if is_storm_like else 0.0
            elif category == "Food Delivery":
                demand_factor += 0.03 * rain_sensitivity if is_light_rain else 0.0
                demand_factor += 0.08 * rain_sensitivity if is_moderate_rain else 0.0
                demand_factor += 0.17 * rain_sensitivity if is_heavy_rain else 0.0
                demand_factor += 0.09 * heat_sensitivity if is_extreme_heat else 0.0
                demand_factor += 0.06 * cold_sensitivity if is_extreme_cold else 0.0
                amount_factor += 0.015 if is_moderate_rain else 0.0
                amount_factor += 0.030 if is_bad_weather else 0.0
                completion_delta -= 0.012 if is_bad_weather else 0.0
                completion_delta -= 0.008 if is_storm_like else 0.0
            elif category == "Grocery":
                demand_factor += 0.015 * rain_sensitivity if is_light_rain else 0.0
                demand_factor += 0.045 * rain_sensitivity if is_moderate_rain else 0.0
                demand_factor += 0.090 * rain_sensitivity if is_heavy_rain else 0.0
                demand_factor += 0.045 * heat_sensitivity if is_extreme_heat else 0.0
                amount_factor += 0.020 if is_moderate_rain else 0.0
                amount_factor += 0.070 if is_bad_weather else 0.0
                completion_delta -= 0.006 if is_bad_weather else 0.0
                completion_delta -= 0.006 if is_heavy_rain or is_high_wind else 0.0
            elif category == "E-Commerce":
                demand_factor += 0.018 * rain_sensitivity if is_moderate_rain or is_heavy_rain else 0.0
                demand_factor += 0.030 * heat_sensitivity if is_extreme_heat else 0.0
                demand_factor += 0.020 * cold_sensitivity if is_extreme_cold else 0.0
                amount_factor += 0.010 if is_bad_weather else 0.0
                completion_delta -= 0.005 if is_bad_weather else 0.0
            else:
                demand_factor += 0.004 if is_bad_weather else 0.0

            demand[market_id, day_index, cat_pos] = demand_factor
            amount[market_id, day_index, cat_pos] = amount_factor
            completion[market_id, day_index, cat_pos] = completion_delta

    return WeatherEffects(
        enabled=True,
        start_date=start,
        demand_multiplier=demand,
        amount_multiplier=amount,
        completion_adjustment=completion,
    )


def weather_day_probabilities(
    base_probabilities: np.ndarray,
    dates: np.ndarray,
    market_id: int,
    category: str,
    weather_effects: WeatherEffects,
) -> np.ndarray:
    if not weather_effects.enabled:
        return base_probabilities
    day_indices = (dates - weather_effects.start_date).astype("timedelta64[D]").astype(int)
    multipliers = weather_effects.demand_multiplier[market_id, day_indices, CATEGORIES.index(category)]
    return normalize(base_probabilities * multipliers)


def weather_vector(
    weather_effects: WeatherEffects,
    market_ids: np.ndarray,
    dates: np.ndarray,
    categories: np.ndarray,
    array: np.ndarray,
    default: float,
) -> np.ndarray:
    if not weather_effects.enabled:
        return np.full(len(categories), default, dtype=np.float64)
    day_indices = (dates - weather_effects.start_date).astype("timedelta64[D]").astype(int)
    cat_indices = category_index(categories)
    return array[market_ids, day_indices, cat_indices]


def hour_probabilities(category: str) -> np.ndarray:
    hours = np.arange(24)
    weights = np.ones(24, dtype=np.float64) * 0.25
    if category == "Food Delivery":
        weights += 1.8 * np.exp(-((hours - 12) ** 2) / 8)
        weights += 2.4 * np.exp(-((hours - 19) ** 2) / 10)
    elif category == "Ride Hailing":
        weights += 2.0 * np.exp(-((hours - 8) ** 2) / 6)
        weights += 2.0 * np.exp(-((hours - 18) ** 2) / 8)
        weights += 0.9 * np.exp(-((hours - 23) ** 2) / 5)
    elif category == "E-Commerce":
        weights += 1.6 * np.exp(-((hours - 21) ** 2) / 14)
        weights += 0.7 * np.exp(-((hours - 13) ** 2) / 18)
    elif category == "Grocery":
        weights += 1.4 * np.exp(-((hours - 11) ** 2) / 14)
        weights += 1.2 * np.exp(-((hours - 17) ** 2) / 14)
    else:
        weights += 0.8 * np.exp(-((hours - 20) ** 2) / 20)
        weights += 0.5 * np.exp(-((hours - 9) ** 2) / 20)
    return normalize(weights)


def generate_platforms(rng: np.random.Generator, primary_devices: np.ndarray, agents: dict) -> np.ndarray:
    out = np.empty(len(primary_devices), dtype=object)
    ios_mask = primary_devices == "iOS"
    android_mask = ~ios_mask
    ios_choices = np.array([agents["ios"], agents["web"], agents["android"]], dtype=object)
    android_choices = np.array([agents["android"], agents["lite"], agents["web"], agents["ios"]], dtype=object)
    out[ios_mask] = weighted_choice(rng, ios_choices, np.array([0.78, 0.20, 0.02]), int(ios_mask.sum()))
    out[android_mask] = weighted_choice(rng, android_choices, np.array([0.58, 0.25, 0.16, 0.01]), int(android_mask.sum()))
    return out


def generate_amounts(
    rng: np.random.Generator,
    categories: np.ndarray,
    hours: np.ndarray,
    month_number: int,
    amount_multiplier: np.ndarray | None = None,
) -> np.ndarray:
    amounts = np.empty(len(categories), dtype=np.float64)
    for category in CATEGORIES:
        mask = categories == category
        size = int(mask.sum())
        if size == 0:
            continue
        if category == "Food Delivery":
            base = 5 + rng.gamma(3.2, 6.4, size=size)
            meal = np.isin(hours[mask], [11, 12, 13, 18, 19, 20])
            base *= np.where(meal, 1.12, 1.0)
            amounts[mask] = np.clip(base, 5, 95)
        elif category == "Grocery":
            base = 12 + rng.gamma(4.4, 12.5, size=size)
            amounts[mask] = np.clip(base, 12, 260)
        elif category == "Ride Hailing":
            base = 4 + rng.gamma(2.4, 7.8, size=size)
            peak = np.isin(hours[mask], [7, 8, 9, 17, 18, 19, 22, 23])
            base *= np.where(peak, 1.28, 1.0)
            amounts[mask] = np.clip(base, 4, 180)
        elif category == "E-Commerce":
            base = rng.lognormal(mean=4.15, sigma=0.78, size=size)
            if month_number in (11, 12):
                base *= 1.12
            amounts[mask] = np.clip(base, 8, 720)
        else:
            large_transfer = rng.random(size) < 0.28
            base = 3 + rng.gamma(2.0, 9.5, size=size)
            base[large_transfer] = rng.lognormal(mean=4.15, sigma=0.90, size=int(large_transfer.sum()))
            amounts[mask] = np.clip(base, 2, 1000)
    if amount_multiplier is not None:
        amounts *= amount_multiplier
    return np.round(amounts, 2)


def generate_statuses(
    rng: np.random.Generator,
    categories: np.ndarray,
    platforms: np.ndarray,
    ratings: np.ndarray,
    amounts: np.ndarray,
    hours: np.ndarray,
    config: dict,
    completion_adjustment: np.ndarray | None = None,
) -> np.ndarray:
    complete = np.array([config["categories"][category]["complete_rate"] for category in categories], dtype=np.float64)
    complete += (ratings - 4.1) * 0.035
    if completion_adjustment is not None:
        complete += completion_adjustment
    complete -= np.where(np.char.find(platforms.astype(str), "Web Portal") >= 0, 0.018, 0.0)
    complete -= np.where((categories == "Ride Hailing") & np.isin(hours, [8, 18, 23]), 0.025, 0.0)
    complete -= np.where((categories == "E-Commerce") & (amounts > 220), 0.020, 0.0)
    complete = np.clip(complete, 0.78, 0.988)

    refund_bias = np.select(
        [
            categories == "E-Commerce",
            categories == "Grocery",
            categories == "Food Delivery",
            categories == "Digital Wallet",
        ],
        [0.68, 0.48, 0.35, 0.10],
        default=0.25,
    )
    failed_or_refunded = rng.random(len(categories)) >= complete
    refund = rng.random(len(categories)) < refund_bias
    statuses = np.full(len(categories), "Completed", dtype=object)
    statuses[failed_or_refunded & refund] = "Refunded"
    statuses[failed_or_refunded & ~refund] = "Failed"
    return statuses


def fraud_behavior_mask(
    rng: np.random.Generator,
    categories: np.ndarray,
    user_segments: np.ndarray,
    lifecycle: np.ndarray,
    hours: np.ndarray,
) -> np.ndarray:
    propensity = np.full(len(categories), 0.0045, dtype=np.float64)
    propensity += np.where(categories == "Digital Wallet", 0.0105, 0.0)
    propensity += np.where(categories == "E-Commerce", 0.0070, 0.0)
    propensity += np.where(categories == "Ride Hailing", 0.0010, 0.0)
    propensity += np.where(categories == "Food Delivery", 0.0020, 0.0)
    propensity += np.where(categories == "Grocery", 0.0015, 0.0)
    propensity += np.where(user_segments == "New", 0.0090, 0.0)
    propensity += np.where(lifecycle == "At Risk", 0.0040, 0.0)
    propensity += np.where(np.isin(hours, [0, 1, 2, 3, 23]), 0.0030, 0.0)
    return rng.random(len(categories)) < np.clip(propensity, 0.0, 0.026)


def concentrate_fraud_users(
    rng: np.random.Generator,
    user_ids: np.ndarray,
    market_ids: np.ndarray,
    categories: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    out = user_ids.copy()
    for market_id in np.unique(market_ids[mask]):
        market_mask = mask & (market_ids == market_id)
        positions = np.flatnonzero(market_mask)
        if len(positions) < 4:
            continue
        for category in ("Digital Wallet", "E-Commerce"):
            category_positions = positions[categories[positions] == category]
            if len(category_positions) < 4:
                continue
            n_anchors = max(1, len(category_positions) // 22)
            anchors = rng.choice(category_positions, size=n_anchors, replace=False)
            out[category_positions] = rng.choice(out[anchors], size=len(category_positions), replace=True)
        for category, anchor_divisor in (
            ("Ride Hailing", 24),
            ("Food Delivery", 28),
            ("Grocery", 34),
        ):
            category_positions = positions[categories[positions] == category]
            if len(category_positions) < 6:
                continue
            n_anchors = max(1, len(category_positions) // anchor_divisor)
            anchors = rng.choice(category_positions, size=n_anchors, replace=False)
            out[category_positions] = rng.choice(out[anchors], size=len(category_positions), replace=True)
    return out


def cluster_fraud_timestamps(
    rng: np.random.Generator,
    timestamp_dt: np.ndarray,
    user_ids: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    out = timestamp_dt.copy()
    suspicious_users, user_counts = np.unique(user_ids[mask], return_counts=True)
    for user_id in suspicious_users[user_counts >= 3]:
        positions = np.flatnonzero(mask & (user_ids == user_id))
        if len(positions) < 3:
            continue
        base_position = int(rng.choice(positions))
        base_hour = out[base_position].astype("datetime64[h]")
        offsets = rng.integers(0, 1800, size=len(positions)).astype("timedelta64[s]")
        out[positions] = (base_hour + offsets).astype("datetime64[us]")
    return out


def apply_fraud_behavior(
    rng: np.random.Generator,
    mask: np.ndarray,
    categories: np.ndarray,
    amounts: np.ndarray,
    statuses: np.ndarray,
    platforms: np.ndarray,
    referrals: np.ndarray,
    agents: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if not mask.any():
        return amounts, statuses, platforms, referrals

    adjusted_amounts = amounts.copy()
    adjusted_statuses = statuses.copy()
    adjusted_platforms = platforms.copy()
    adjusted_referrals = referrals.copy()

    amount_multiplier = np.ones(len(categories), dtype=np.float64)
    amount_multiplier[mask & (categories == "Digital Wallet")] = rng.lognormal(
        mean=1.44,
        sigma=0.48,
        size=int((mask & (categories == "Digital Wallet")).sum()),
    )
    amount_multiplier[mask & (categories == "E-Commerce")] = rng.lognormal(
        mean=0.96,
        sigma=0.40,
        size=int((mask & (categories == "E-Commerce")).sum()),
    )
    amount_multiplier[mask & np.isin(categories, ["Food Delivery", "Grocery", "Ride Hailing"])] = rng.lognormal(
        mean=0.16,
        sigma=0.25,
        size=int((mask & np.isin(categories, ["Food Delivery", "Grocery", "Ride Hailing"])).sum()),
    )
    amount_multiplier[mask & (categories == "Ride Hailing")] *= 0.94
    amount_multiplier[mask & (categories == "Food Delivery")] *= 1.03
    amount_multiplier[mask & (categories == "Grocery")] *= 1.06
    adjusted_amounts = np.round(adjusted_amounts * amount_multiplier, 2)
    adjusted_amounts[categories == "Digital Wallet"] = np.clip(adjusted_amounts[categories == "Digital Wallet"], 2, 1800)
    adjusted_amounts[categories == "E-Commerce"] = np.clip(adjusted_amounts[categories == "E-Commerce"], 8, 1200)
    adjusted_amounts[categories == "Grocery"] = np.clip(adjusted_amounts[categories == "Grocery"], 12, 360)
    adjusted_amounts[categories == "Food Delivery"] = np.clip(adjusted_amounts[categories == "Food Delivery"], 5, 130)
    adjusted_amounts[categories == "Ride Hailing"] = np.clip(adjusted_amounts[categories == "Ride Hailing"], 4, 240)

    status_draw = rng.random(len(categories))
    digital_mask = mask & (categories == "Digital Wallet")
    ecommerce_mask = mask & (categories == "E-Commerce")
    other_mask = mask & ~np.isin(categories, ["Digital Wallet", "E-Commerce"])
    adjusted_statuses[digital_mask & (status_draw < 0.65)] = "Failed"
    adjusted_statuses[digital_mask & (status_draw >= 0.65) & (status_draw < 0.85)] = "Refunded"
    adjusted_statuses[ecommerce_mask & (status_draw < 0.35)] = "Failed"
    adjusted_statuses[ecommerce_mask & (status_draw >= 0.35) & (status_draw < 0.80)] = "Refunded"
    ride_mask = mask & (categories == "Ride Hailing")
    food_mask = mask & (categories == "Food Delivery")
    grocery_mask = mask & (categories == "Grocery")
    adjusted_statuses[ride_mask & (status_draw < 0.33)] = "Failed"
    adjusted_statuses[ride_mask & (status_draw >= 0.33) & (status_draw < 0.54)] = "Refunded"
    adjusted_statuses[food_mask & (status_draw < 0.39)] = "Failed"
    adjusted_statuses[food_mask & (status_draw >= 0.39) & (status_draw < 0.64)] = "Refunded"
    adjusted_statuses[grocery_mask & (status_draw < 0.36)] = "Failed"
    adjusted_statuses[grocery_mask & (status_draw >= 0.36) & (status_draw < 0.60)] = "Refunded"
    adjusted_statuses[other_mask & (status_draw < 0.38)] = "Failed"
    adjusted_statuses[other_mask & (status_draw >= 0.38) & (status_draw < 0.62)] = "Refunded"

    platform_draw = rng.random(len(categories))
    adjusted_platforms[mask & (platform_draw < 0.34)] = agents["web"]
    adjusted_platforms[mask & (platform_draw >= 0.34) & (platform_draw < 0.54)] = agents["lite"]

    referral_draw = rng.random(len(categories))
    adjusted_referrals[mask & (referral_draw < 0.42)] = "Social Ad"
    adjusted_referrals[mask & (referral_draw >= 0.42) & (referral_draw < 0.72)] = "Email Promo"
    adjusted_referrals[mask & (referral_draw >= 0.72)] = "Push Notification"
    return adjusted_amounts, adjusted_statuses, adjusted_platforms, adjusted_referrals


def generate_referrals(
    rng: np.random.Generator,
    acquisition: np.ndarray,
    lifecycle: np.ndarray,
    is_promo: np.ndarray,
) -> np.ndarray:
    referrals = acquisition.astype(object).copy()
    promo_mask = is_promo & (rng.random(len(acquisition)) < 0.46)
    referrals[promo_mask] = weighted_choice(rng, np.array(["Email Promo", "Push Notification", "Social Ad"], dtype=object), np.array([0.42, 0.42, 0.16]), int(promo_mask.sum()))
    retained_mask = (lifecycle == "Retained") & (rng.random(len(acquisition)) < 0.24)
    referrals[retained_mask] = "Push Notification"
    return referrals


def write_interaction_batch(
    batch: dict,
    month_key: str,
    part_number: int,
    output_dir: Path,
) -> None:
    month_dir = output_dir / "nova_interactions" / f"month={month_key}"
    month_dir.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(batch).with_columns(
        pl.col("Timestamp_dt").dt.strftime("%Y-%m-%d %H:%M:%S").alias("Timestamp"),
        pl.col("Timestamp_dt").dt.date().alias("Date"),
        pl.col("Timestamp_dt").dt.truncate("1mo").alias("Month"),
        pl.col("Timestamp_dt").dt.hour().cast(pl.Int8).alias("Hour"),
    )
    ordered = [
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
    df.select(ordered).write_parquet(month_dir / f"part-{part_number:04d}.parquet", compression="zstd")


def generate_interactions(
    output_dir: Path,
    config: dict,
    months: list[date],
    month_counts: dict[str, int],
    lookup: dict,
    user_pools: dict,
    service_pools: dict,
    weather_effects: WeatherEffects,
    rng: np.random.Generator,
    batch_size: int,
    enable_fraud_behavior: bool,
) -> None:
    category_values = np.array(CATEGORIES, dtype=object)
    global_row_start = 0
    agents = config["platform_user_agents"]
    markets = np.arange(1, 17)

    for month in months:
        month_key = month.strftime("%Y-%m")
        rows_remaining = month_counts[month_key]
        part_number = 0
        month_market_weights = normalize(
            lookup["market_weights"] * np.array([market_month_multiplier(month, int(market_id)) for market_id in markets], dtype=np.float64)
        )

        while rows_remaining:
            size = min(batch_size, rows_remaining)
            ordinals = np.arange(global_row_start, global_row_start + size, dtype=np.int64)
            transaction_uuid = np.array(
                [f"00000000-0000-4000-8000-{int(value):012x}" for value in ordinals],
                dtype=object,
            )

            market_ids = weighted_choice(rng, markets, month_market_weights, size)
            user_ids = np.empty(size, dtype=np.int64)
            for market_id in markets:
                mask = market_ids == market_id
                if mask.any():
                    candidates, probabilities = user_pools[(month_key, int(market_id))]
                    user_ids[mask] = weighted_choice(rng, candidates, probabilities, int(mask.sum()))

            user_index = user_ids - 1
            primary_devices = lookup["primary_devices"][user_index]
            acquisition = lookup["acquisition_sources"][user_index]
            user_segments = lookup["user_segments"][user_index]
            lifecycle = lookup["lifecycle_segments"][user_index]
            membership = lookup["membership_tiers"][user_index]

            categories = np.empty(size, dtype=object)
            for market_id in markets:
                mask = market_ids == market_id
                if mask.any():
                    categories[mask] = weighted_choice(
                        rng,
                        category_values,
                        market_category_probs(config, month_key, int(market_id)),
                        int(mask.sum()),
                    )
            service_ids = np.empty(size, dtype=np.int64)
            for market_id in markets:
                market_mask = market_ids == market_id
                if not market_mask.any():
                    continue
                for category in CATEGORIES:
                    mask = market_mask & (categories == category)
                    if mask.any():
                        candidates, probabilities = service_pools[(int(market_id), category)]
                        service_ids[mask] = weighted_choice(rng, candidates, probabilities, int(mask.sum()))

            service_index = service_ids - 1
            service_ratings = lookup["service_ratings"][service_index]
            service_tiers = lookup["service_tiers"][service_index]

            dates = np.empty(size, dtype="datetime64[D]")
            hours = np.empty(size, dtype=np.int16)
            for market_id in markets:
                market_mask = market_ids == market_id
                if not market_mask.any():
                    continue
                for category in CATEGORIES:
                    mask = market_mask & (categories == category)
                    if not mask.any():
                        continue
                    month_dates, _, day_probs = day_probabilities(month, category)
                    day_probs = weather_day_probabilities(day_probs, month_dates, int(market_id), category, weather_effects)
                    chosen_day_idx = rng.choice(np.arange(len(month_dates)), size=int(mask.sum()), replace=True, p=day_probs)
                    dates[mask] = month_dates[chosen_day_idx]
                    hours[mask] = rng.choice(np.arange(24), size=int(mask.sum()), replace=True, p=hour_probabilities(category))

            seconds = (hours.astype(np.int64) * 3600) + rng.integers(0, 3600, size=size)
            timestamp_dt = (dates.astype("datetime64[s]") + seconds.astype("timedelta64[s]")).astype("datetime64[us]")
            is_promo = ((month.month in (11, 12)) & (categories == "E-Commerce")) | (
                (month.month in (6, 7, 8)) & np.isin(categories, ["Food Delivery", "Ride Hailing"])
            )

            fraud_mask = np.zeros(size, dtype=bool)
            if enable_fraud_behavior:
                fraud_mask = fraud_behavior_mask(rng, categories, user_segments, lifecycle, hours)
                user_ids = concentrate_fraud_users(rng, user_ids, market_ids, categories, fraud_mask)
                timestamp_dt = cluster_fraud_timestamps(rng, timestamp_dt, user_ids, fraud_mask)
                user_index = user_ids - 1
                primary_devices = lookup["primary_devices"][user_index]
                acquisition = lookup["acquisition_sources"][user_index]
                user_segments = lookup["user_segments"][user_index]
                lifecycle = lookup["lifecycle_segments"][user_index]
                membership = lookup["membership_tiers"][user_index]

            amount_multiplier = weather_vector(
                weather_effects,
                market_ids,
                dates,
                categories,
                weather_effects.amount_multiplier,
                1.0,
            )
            category_market_amount_multiplier = np.ones(size, dtype=np.float64)
            for market_id in markets:
                market_mask = market_ids == market_id
                if not market_mask.any():
                    continue
                for category in CATEGORIES:
                    mask = market_mask & (categories == category)
                    if mask.any():
                        category_market_amount_multiplier[mask] = 0.86 + 0.14 * MARKET_CATEGORY_AFFINITY[int(market_id)][category]
            amount_multiplier *= MARKET_AMOUNT_MULTIPLIER[market_ids] * category_market_amount_multiplier * user_amount_multiplier(membership, lifecycle)
            completion_adjustment = weather_vector(
                weather_effects,
                market_ids,
                dates,
                categories,
                weather_effects.completion_adjustment,
                0.0,
            )
            completion_adjustment += MARKET_COMPLETION_ADJUSTMENT[market_ids] + user_completion_adjustment(membership, lifecycle)
            platforms = generate_platforms(rng, primary_devices, agents)
            amounts = generate_amounts(rng, categories, hours, month.month, amount_multiplier)
            statuses = generate_statuses(rng, categories, platforms, service_ratings, amounts, hours, config, completion_adjustment)
            referrals = generate_referrals(rng, acquisition, lifecycle, is_promo)
            if enable_fraud_behavior:
                amounts, statuses, platforms, referrals = apply_fraud_behavior(
                    rng,
                    fraud_mask,
                    categories,
                    amounts,
                    statuses,
                    platforms,
                    referrals,
                    agents,
                )

            market_index = market_ids - 1
            gps_lat = np.round(lookup["market_lats"][market_index] + rng.normal(0.0, 0.11, size=size), 5)
            gps_long = np.round(lookup["market_longs"][market_index] + rng.normal(0.0, 0.14, size=size), 5)

            write_interaction_batch(
                {
                    "Transaction_UUID": transaction_uuid,
                    "User_ID": user_ids,
                    "Service_ID": service_ids,
                    "Category": categories,
                    "Amount_USD": amounts,
                    "Status": statuses,
                    "Platform_User_Agent": platforms,
                    "Referral_Source": referrals,
                    "GPS_Lat": gps_lat,
                    "GPS_Long": gps_long,
                    "Timestamp_dt": timestamp_dt,
                    "Market_ID": market_ids,
                    "Market_Name": lookup["market_names"][market_index],
                    "Region": lookup["market_regions"][market_index],
                    "Acquisition_Source": acquisition,
                    "User_Segment": user_segments,
                    "Lifecycle_Segment": lifecycle,
                    "Service_Tier": service_tiers,
                    "Is_Promo_Period": is_promo,
                },
                month_key,
                part_number,
                output_dir,
            )

            rows_remaining -= size
            global_row_start += size
            part_number += 1
            print(f"generated {month_key} part {part_number}: {size:,} rows")


def write_non_partitioned_interactions(output_dir: Path) -> None:
    interaction_files = sorted((output_dir / "nova_interactions").glob("month=*/part-*.parquet"))
    if not interaction_files:
        raise SystemExit(f"No partitioned interaction parquet files found under {output_dir / 'nova_interactions'}")
    pl.scan_parquet([str(path) for path in interaction_files], hive_partitioning=False).sink_parquet(
        output_dir / "nova_interactions.parquet",
        compression="zstd",
        maintain_order=True,
    )


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_config(config_path)
    target_rows = args.target_rows or int(config["target_rows"])
    batch_size = args.batch_size or int(config["batch_size"])

    raw_dir = Path(config["paths"]["raw_dir"])
    output_dir = Path(args.output_dir or config["paths"]["corrected_dir"])
    paths = Paths(raw_dir=raw_dir, output_dir=output_dir)

    if paths.output_dir.exists():
        if not args.overwrite:
            raise SystemExit(f"{paths.output_dir} already exists. Pass --overwrite to replace it.")
        shutil.rmtree(paths.output_dir)
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(int(config["seed"]))
    months = month_starts(config["dates"]["start"], config["dates"]["end"])
    month_counts = allocate_counts(target_rows, config["dates"]["monthly_shares"], months)

    raw_users = pl.read_parquet(paths.raw_dir / "nova_users.parquet")
    raw_services = pl.read_parquet(paths.raw_dir / "nova_services.parquet")

    markets = create_markets(config)
    users = generate_users(raw_users, markets, config, rng)
    services = generate_services(raw_services, markets, config, rng)

    markets.write_parquet(paths.output_dir / "nova_markets.parquet", compression="zstd")
    users.write_parquet(paths.output_dir / "nova_users.parquet", compression="zstd")
    services.write_parquet(paths.output_dir / "nova_services.parquet", compression="zstd")

    lookup = build_lookup_arrays(users, services, markets)
    user_pools = precompute_user_pools(lookup, months)
    service_pools = precompute_service_pools(lookup)
    weather_effects = load_weather_effects(config, args.enable_weather_effects)
    generate_interactions(
        paths.output_dir,
        config,
        months,
        month_counts,
        lookup,
        user_pools,
        service_pools,
        weather_effects,
        rng,
        batch_size,
        args.enable_fraud_behavior,
    )
    write_non_partitioned_interactions(paths.output_dir)

    metadata = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "seed": int(config["seed"]),
        "target_rows": target_rows,
        "batch_size": batch_size,
        "enable_weather_effects": bool(args.enable_weather_effects),
        "enable_fraud_behavior": bool(args.enable_fraud_behavior),
        "month_counts": month_counts,
        "source_raw_dir": str(paths.raw_dir),
        "output_dir": str(paths.output_dir),
    }
    (paths.output_dir / "_generation_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"corrected dataset written to {paths.output_dir}")


if __name__ == "__main__":
    main()
