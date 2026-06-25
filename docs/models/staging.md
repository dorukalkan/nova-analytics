---
icon: lucide/arrows-up-from-line
title: Staging Models
description: Clean source interfaces for Nova analytics
---

# Staging Models

Staging models are the clean interface between raw/corrected data and the analysis pipeline. They standardize names, preserve source grain, and add basic validation without introducing business scoring logic.

For a portfolio audience, the important point is simple: every analysis page starts from a stable set of source-facing models instead of repeatedly cleaning raw fields inside dashboard queries.

!!! abstract "Layer purpose"

    The staging layer answers: can the rest of the project rely on consistent transaction, user, service, market, and external-context fields?

## Nova Core Entities

| Model | Grain | Pipeline role | Main analyses supported |
| --- | --- | --- | --- |
| `stg_interactions` | one row per transaction | Standardizes transaction amount, status, timestamp, category, market, user, service, platform, lifecycle, and promo fields | Executive Summary, Marketplace, Demand Drivers, Category Performance, Customer/RFM, Repeat & Risk |
| `stg_users` | one row per user | Standardizes membership, acquisition, lifecycle, device, market, and join-date fields | Customer Analysis, RFM Analysis, Customer Repeat & Risk |
| `stg_services` | one row per service | Standardizes category, rating, market, service tier, and popularity fields | Category Performance, Demand Drivers, service supply features |
| `stg_markets` | one row per market | Standardizes city market names, regions, coordinates, and market configuration fields | Marketplace Analysis, Demand Drivers, market clustering |

## External Context Staging

| Model | Grain | Pipeline role | Main analyses supported |
| --- | --- | --- | --- |
| `stg_geo_market_country_lookup` | one row per Nova market | Bridges Nova city markets to country identifiers | Marketplace Analysis, Demand Drivers |
| `stg_geo_weather_daily` | one row per market per day | Adds daily local weather features | Demand Drivers, weather sensitivity |
| `stg_geo_world_bank_indicators` | one row per country per indicator | Provides macro indicators before pivoting | Marketplace opportunity scoring |
| `stg_geo_country_metadata` | one row per country | Adds country labels, currency, region, and timezone context | Marketplace Analysis and dashboard labeling |

## Business Relevance

The staging layer keeps business logic from being scattered across dashboards. For example, category names, transaction statuses, service tiers, and user lifecycle fields are standardized once, then reused throughout the project. That makes the analyses easier to trust and easier to explain.

## Quality Controls

Staging tests cover the fundamentals: unique transaction, user, service, and market keys; accepted values for categories, statuses, user segments, and service tiers; required timestamps and dates; and relationships from transactions to users and services. These tests are the first quality gate before the data is aggregated into business metrics.
