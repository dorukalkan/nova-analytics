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


@dataclass(frozen=True)
class Paths:
    raw_dir: Path
    output_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate corrected Nova parquet tables before BigQuery ingestion.")
    parser.add_argument("--config", default="config/nova_correction.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--target-rows", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
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
    power_mask = user_segment == "Power"
    regular_mask = user_segment == "Regular"
    membership[regular_mask & (rng.random(n_users) < 0.28)] = "Gold"
    membership[power_mask & (rng.random(n_users) < 0.52)] = "Gold"
    membership[power_mask & (rng.random(n_users) < 0.30)] = "Platinum"

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
    at_risk_mask = (user_segment == "Casual") & (rng.random(n_users) < 0.28)
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

    category_weights = normalize(np.array([config["categories"][category]["base_share"] for category in CATEGORIES]))
    categories = weighted_choice(rng, np.array(CATEGORIES, dtype=object), category_weights, n_services)

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
    weights = np.select(
        [
            segment == "New",
            segment == "Casual",
            segment == "Regular",
            segment == "Power",
        ],
        [0.75, 0.38, 1.45, 5.80],
        default=0.0,
    ).astype(np.float64)
    return weights


def precompute_user_pools(lookup: dict, months: list[date]) -> dict[tuple[str, int], tuple[np.ndarray, np.ndarray]]:
    pools: dict[tuple[str, int], tuple[np.ndarray, np.ndarray]] = {}
    user_ids = lookup["user_ids"]
    join_dates = lookup["user_join_dates"]
    market_ids = lookup["user_market_ids"]
    segments = lookup["user_segments"]
    weights = user_weight(segments)
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
    return np.round(amounts, 2)


def generate_statuses(
    rng: np.random.Generator,
    categories: np.ndarray,
    platforms: np.ndarray,
    ratings: np.ndarray,
    amounts: np.ndarray,
    hours: np.ndarray,
    config: dict,
) -> np.ndarray:
    complete = np.array([config["categories"][category]["complete_rate"] for category in categories], dtype=np.float64)
    complete += (ratings - 4.1) * 0.035
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
    rng: np.random.Generator,
    batch_size: int,
) -> None:
    category_values = np.array(CATEGORIES, dtype=object)
    global_row_start = 0
    agents = config["platform_user_agents"]
    markets = np.arange(1, 17)

    for month in months:
        month_key = month.strftime("%Y-%m")
        rows_remaining = month_counts[month_key]
        part_number = 0
        category_probs = category_probs_for_month(config, month_key)

        while rows_remaining:
            size = min(batch_size, rows_remaining)
            ordinals = np.arange(global_row_start, global_row_start + size, dtype=np.int64)
            transaction_uuid = np.array(
                [f"00000000-0000-4000-8000-{int(value):012x}" for value in ordinals],
                dtype=object,
            )

            market_ids = weighted_choice(rng, markets, lookup["market_weights"], size)
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

            categories = weighted_choice(rng, category_values, category_probs, size)
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
            for category in CATEGORIES:
                mask = categories == category
                if not mask.any():
                    continue
                month_dates, _, day_probs = day_probabilities(month, category)
                chosen_day_idx = rng.choice(np.arange(len(month_dates)), size=int(mask.sum()), replace=True, p=day_probs)
                dates[mask] = month_dates[chosen_day_idx]
                hours[mask] = rng.choice(np.arange(24), size=int(mask.sum()), replace=True, p=hour_probabilities(category))

            seconds = (hours.astype(np.int64) * 3600) + rng.integers(0, 3600, size=size)
            timestamp_dt = (dates.astype("datetime64[s]") + seconds.astype("timedelta64[s]")).astype("datetime64[us]")
            is_promo = ((month.month in (11, 12)) & (categories == "E-Commerce")) | (
                (month.month in (6, 7, 8)) & np.isin(categories, ["Food Delivery", "Ride Hailing"])
            )

            platforms = generate_platforms(rng, primary_devices, agents)
            amounts = generate_amounts(rng, categories, hours, month.month)
            statuses = generate_statuses(rng, categories, platforms, service_ratings, amounts, hours, config)
            referrals = generate_referrals(rng, acquisition, lifecycle, is_promo)

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
    generate_interactions(paths.output_dir, config, months, month_counts, lookup, user_pools, service_pools, rng, batch_size)

    metadata = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "seed": int(config["seed"]),
        "target_rows": target_rows,
        "batch_size": batch_size,
        "month_counts": month_counts,
        "source_raw_dir": str(paths.raw_dir),
        "output_dir": str(paths.output_dir),
    }
    (paths.output_dir / "_generation_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"corrected dataset written to {paths.output_dir}")


if __name__ == "__main__":
    main()
