---
icon: lucide/package-open
title: Intermediate Models
description: Reusable dbt business logic behind the Nova analyses
---

# Intermediate dbt Models

Intermediate models are the reusable logic layer of the Nova project. They turn clean staged sources into shared analytical building blocks: market context, complete date/category spines, daily demand metrics, service health, customer metrics, RFM scores, and repeat-behavior features.

These models are not the final dashboard contract. Their job is to make the final marts consistent, tested, and easier to reason about.

!!! abstract "Layer purpose"

    The intermediate layer answers: what reusable business logic should be defined once so every dashboard and notebook uses the same calculations?

## Market Context and Calendar Logic

| Models | What they do | Used by |
| --- | --- | --- |
| `int_geo_country_macro_pivot` | Pivots long-form World Bank indicators into one country-level row | Marketplace Analysis |
| `int_geo_market_context` | Combines Nova market attributes, country lookup, country metadata, and macro indicators | Marketplace Analysis, Demand Drivers |
| `int_geo_date_spine` | Creates a complete calendar spine from the weather date range | Demand Drivers |

This group makes market analysis comparable. Instead of treating each city as only a transaction label, the pipeline gives each market country, macro, calendar, and geography context.

## Demand Foundations

| Models | What they do | Used by |
| --- | --- | --- |
| `int_geo_market_day_metrics` | Aggregates transactions to market-day demand, GMV, activity, status, promo, and platform metrics | Marketplace Analysis |
| `int_geo_market_category_day_metrics` | Aggregates transactions to market-category-day metrics | Demand Drivers, demand modeling |
| `int_geo_market_category_hour_metrics` | Aggregates category demand by market and hour | Demand Drivers |
| `int_geo_market_category_spine` | Builds a complete market/category/date grid so missing demand is explicit | Demand Drivers |
| `int_geo_service_supply_by_market_category` | Adds supply-side context such as active services, ratings, popularity, and service-tier mix | Marketplace Analysis, Demand Drivers |

This is the analytical base for the demand-driver work. It lets the project compare demand against weather, time, service supply, market context, and category behavior at consistent grains.

## Service and Category Health

| Models | What they do | Used by |
| --- | --- | --- |
| `int_services_enriched` | Adds market and country context to services | Category Performance, Customer Repeat & Risk |
| `int_service_interactions` | Joins transactions to enriched service context | Category Performance, repeat behavior, fraud features |
| `int_service_health` | Calculates service-level interaction, amount, success, failure, refund, and rating metrics | Category Performance |
| `int_service_risk` | Classifies services into risk segments using success, failure, refund, and rating signals | Category Performance |
| `int_category_health` | Rolls service health up to category-level performance | Category Performance |
| `int_service_monthly_health` | Tracks service performance over time | Category and service performance monitoring |

This group turns raw service activity into operational intelligence. It supports the category page's main question: which categories are large, reliable, risky, or worth stabilizing before further growth?

## Customer, RFM, and Repeat Logic

| Models | What they do | Used by |
| --- | --- | --- |
| `int_customer_metrics` | Builds customer-level transaction count, spend, order dates, lifetime, category count, and service usage | RFM Analysis |
| `int_rfm_features` | Converts customer history into recency, frequency, and monetary fields | RFM Analysis |
| `int_rfm_scores` | Assigns 1-5 RFM scores used for segment labels | RFM Analysis |
| `int_user_service_repeat_behavior` | Measures repeat behavior at the user-service grain | Customer Repeat & Risk |

This group translates transaction history into customer strategy. It powers segmentation, retention prioritization, and repeat-use metrics without relying on dashboard-only calculations.

## Quality Controls

Intermediate tests focus on grain and relationships: one row per market-day, market-category-day, market-category-hour, market-category-date spine row, and market-category supply row. These checks are important because the final dashboards and notebooks assume that each intermediate model has a stable grain.

!!! tip "Why this matters"

    The intermediate layer is where the project becomes a pipeline rather than a set of charts. Shared definitions for demand, supply, service health, and customer behavior keep the final analysis pages consistent.
