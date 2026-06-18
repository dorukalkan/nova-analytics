---
icon: lucide/package-open
title: Intermediate Models
description: intermediate dbt models documentation
---

# Intermediate dbt Models

This page documents the geography-track intermediate models only. Intermediate models are reusable building blocks for joins, pivots, spines, and base aggregates. They are not the final Power BI contract; the final analysis tables will live in the mart layer.

## Geography Context Models

### int_geo_country_macro_pivot

Pivots long-form World Bank indicators into one row per country. This makes macro context easy to join into market-level models.

**Grain:** one row per `country_iso3`.

**Keys and joins:**

- Primary key: `country_iso3`
- Built from `stg_geo_world_bank_indicators`
- Join to `stg_geo_country_metadata` or market context on `country_iso3`

| Column | Description |
| --- | --- |
| `country_iso3` | ISO 3166-1 alpha-3 country code. |
| `country_name` | World Bank country name. |
| `population_total` | Latest available total population value. |
| `gdp_per_capita_current_usd` | Latest available GDP per capita in current USD. |
| `urban_population_pct` | Latest available urban population share. |
| `internet_users_pct` | Latest available internet users share. |
| `mobile_subscriptions_per_100_people` | Latest available mobile subscriptions per 100 people. |
| `*_year` fields | Source year for each macro indicator. |

**Preview (selected columns, 5 rows):**

| country_iso3 | country_name | population_total | gdp_per_capita_current_usd | urban_population_pct | internet_users_pct | mobile_subscriptions_per_100_people |
| --- | --- | --- | --- | --- | --- | --- |
| ARE | United Arab Emirates | 10986400 | 50273.5060 | 85.8171 | 100.0000 | 203.2064 |
| AUS | Australia | 27196812 | 64603.9856 | 87.6021 | 96.1314 | 112.5810 |
| BRA | Brazil | 211998573 | 10310.5489 | 87.8959 | 84.4635 | 101.9268 |
| GBR | United Kingdom | 69226000 | 53246.3676 | 83.2430 | 95.4721 | 121.6433 |
| IDN | Indonesia | 283487931 | 4925.4305 | 58.7510 | 72.7808 | 122.5149 |

**Tests:** unique and not-null `country_iso3`; not-null macro values.

### int_geo_market_context

Combines Nova market attributes, market-country mapping, country metadata, and pivoted macro indicators.

**Grain:** one row per Nova market.

**Keys and joins:**

- Primary key: `market_id`
- Join to transaction aggregates on `market_id`
- Join to country-level models on `country_iso3`

| Column group | Examples |
| --- | --- |
| Market attributes | `market_id`, `market_name`, `nova_region`, `latitude`, `longitude`, `market_weight`, `growth_multiplier`, `ios_share` |
| Country identifiers | `country_name`, `country_iso2`, `country_iso3`, `world_bank_country_code` |
| Country metadata | `country_region`, `country_subregion`, `country_capital`, `currency_code`, `timezones` |
| Macro indicators | `population_total`, `gdp_per_capita_current_usd`, `urban_population_pct`, `internet_users_pct`, `mobile_subscriptions_per_100_people` |

**Preview (selected columns, 5 rows):**

| market_id | market_name | nova_region | country_iso3 | country_region | country_subregion | market_weight | growth_multiplier | ios_share | gdp_per_capita_current_usd | internet_users_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Singapore | Southeast Asia | SGP | Asia | South-Eastern Asia | 0.070 | 1.08 | 0.55 | 90674.0666 | 94.3776 |
| 2 | Jakarta | Southeast Asia | IDN | Asia | South-Eastern Asia | 0.090 | 1.18 | 0.28 | 4925.4305 | 72.7808 |
| 3 | Manila | Southeast Asia | PHL | Asia | South-Eastern Asia | 0.075 | 1.16 | 0.32 | 3984.8315 | 67.2630 |
| 4 | Bangkok | Southeast Asia | THA | Asia | South-Eastern Asia | 0.065 | 1.12 | 0.36 | 7346.6202 | 90.8672 |
| 5 | Ho Chi Minh City | Southeast Asia | VNM | Asia | South-Eastern Asia | 0.060 | 1.17 | 0.30 | 4717.2903 | 84.1500 |

**Tests:** unique and not-null `market_id`; not-null country and core market context.

## Geography Spines

### int_geo_date_spine

Calendar spine generated from the weather seed date range.

**Grain:** one row per date.

**Keys and joins:**

- Primary key: `order_date`
- Join to market/day models on `order_date`
- Cross-join into complete market/category/date spine

| Column | Description |
| --- | --- |
| `order_date` | Calendar date. |
| `year` | Calendar year. |
| `quarter` | Calendar quarter. |
| `month` | Calendar month number. |
| `year_month` | Year-month label. |
| `day_of_week` | BigQuery day-of-week number. |
| `day_name` | Day name. |
| `is_weekend` | True for Saturday or Sunday. |

**Preview (5 rows):**

| order_date | year | quarter | month | year_month | day_of_week | day_name | is_weekend |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2024-01-01 | 2024 | 1 | 1 | 2024-01 | 2 | Monday | false |
| 2024-01-02 | 2024 | 1 | 1 | 2024-01 | 3 | Tuesday | false |
| 2024-01-03 | 2024 | 1 | 1 | 2024-01 | 4 | Wednesday | false |
| 2024-01-04 | 2024 | 1 | 1 | 2024-01 | 5 | Thursday | false |
| 2024-01-05 | 2024 | 1 | 1 | 2024-01 | 6 | Friday | false |

**Tests:** unique and not-null `order_date`; not-null calendar attributes.

### int_geo_market_category_spine

Complete market/category/date grid for demand modeling and Power BI matrix views.

**Grain:** one row per `market_id + category + order_date`.

**Keys and joins:**

- Primary key: `market_id`, `category`, `order_date`
- Join to market context on `market_id`
- Join to market-category-day metrics on all three grain columns

| Column | Description |
| --- | --- |
| `market_id` | Nova market identifier. |
| `market_name` | Nova market city name. |
| `region` | Nova market region. |
| `category` | Nova service/category label. |
| `order_date` | Calendar date. |

**Preview (5 rows):**

| market_id | market_name | region | category | order_date |
| --- | --- | --- | --- | --- |
| 1 | Singapore | Southeast Asia | Digital Wallet | 2024-01-01 |
| 1 | Singapore | Southeast Asia | Digital Wallet | 2024-01-02 |
| 1 | Singapore | Southeast Asia | Digital Wallet | 2024-01-03 |
| 1 | Singapore | Southeast Asia | Digital Wallet | 2024-01-04 |
| 1 | Singapore | Southeast Asia | Digital Wallet | 2024-01-05 |

**Tests:** not-null grain columns; relationship to `stg_markets`; no duplicate grain rows.

## Geography Aggregates

### int_geo_market_day_metrics

Aggregates Nova interactions to market/day. This is the base demand table for market-level trends.

**Grain:** one row per `market_id + order_date`.

**Keys and joins:**

- Primary key: `market_id`, `order_date`
- Join to market context on `market_id`
- Join to weather on `market_id` and `order_date = weather_date`

| Column group | Examples |
| --- | --- |
| Demand | `transactions`, `gmv_usd`, `avg_transaction_amount_usd`, `active_users` |
| Status | `completed_transactions`, `failed_transactions`, `refunded_transactions`, `completion_rate`, `failed_rate`, `refunded_rate` |
| Promo | `promo_transactions`, `promo_share` |
| Platform | `ios_transactions`, `android_transactions`, `lite_transactions`, `web_transactions`, platform shares |

**Preview (selected columns, 5 rows):**

| market_id | market_name | order_date | transactions | gmv_usd | active_users | completion_rate | promo_share | ios_transaction_share | web_transaction_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Singapore | 2024-01-01 | 6982 | 327844.08 | 6511 | 0.9178 | 0.0000 | 0.4235 | 0.1932 |
| 1 | Singapore | 2024-01-02 | 6875 | 323780.80 | 6367 | 0.9206 | 0.0000 | 0.4407 | 0.1728 |
| 1 | Singapore | 2024-01-03 | 6839 | 316646.11 | 6391 | 0.9158 | 0.0000 | 0.4398 | 0.1768 |
| 1 | Singapore | 2024-01-04 | 6935 | 329871.08 | 6428 | 0.9119 | 0.0000 | 0.4405 | 0.1850 |
| 1 | Singapore | 2024-01-05 | 6896 | 321468.56 | 6409 | 0.9137 | 0.0000 | 0.4365 | 0.1797 |

**Tests:** not-null grain and core metric columns; relationship to `stg_markets`; no duplicate grain rows.

### int_geo_market_category_day_metrics

Aggregates Nova interactions to market/category/day. This is the base demand table for category-specific weather sensitivity.

**Grain:** one row per `market_id + category + order_date`.

**Keys and joins:**

- Primary key: `market_id`, `category`, `order_date`
- Join to `int_geo_market_category_spine` on all grain columns
- Join to service supply on `market_id` and `category`

| Column group | Examples |
| --- | --- |
| Demand | `transactions`, `gmv_usd`, `avg_transaction_amount_usd`, `active_users`, `active_services_with_transactions` |
| Status | `completed_transactions`, `failed_transactions`, `refunded_transactions`, status rates |
| Promo | `promo_transactions`, `promo_share` |
| Service tier | `head_tier_transactions`, `mid_tier_transactions`, `long_tail_tier_transactions`, tier transaction shares |
| Platform | transaction counts and shares for iOS, Android, Lite, and Web |

**Preview (selected columns, 5 rows):**

| market_id | market_name | category | order_date | transactions | gmv_usd | active_users | active_services_with_transactions | completion_rate | promo_share | head_tier_transaction_share | web_transaction_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Singapore | Digital Wallet | 2024-01-01 | 1048 | 44054.69 | 1042 | 291 | 0.9790 | 0.0000 | 0.3197 | 0.1956 |
| 1 | Singapore | Digital Wallet | 2024-01-02 | 825 | 34577.89 | 819 | 262 | 0.9745 | 0.0000 | 0.3297 | 0.1830 |
| 1 | Singapore | Digital Wallet | 2024-01-03 | 814 | 35515.85 | 811 | 246 | 0.9754 | 0.0000 | 0.3231 | 0.1744 |
| 1 | Singapore | Digital Wallet | 2024-01-04 | 781 | 32398.49 | 775 | 254 | 0.9808 | 0.0000 | 0.3303 | 0.1818 |
| 1 | Singapore | Digital Wallet | 2024-01-05 | 843 | 37959.87 | 833 | 266 | 0.9858 | 0.0000 | 0.3120 | 0.1673 |

**Tests:** not-null grain and core metric columns; relationship to `stg_markets`; no duplicate grain rows.

### int_geo_service_supply_by_market_category

Aggregates the service dimension to market/category supply signals.

**Grain:** one row per `market_id + category`.

**Keys and joins:**

- Primary key: `market_id`, `category`
- Join to market/category/day models on `market_id` and `category`
- Used to add supply-side context to final feature marts

| Column | Description |
| --- | --- |
| `market_id` | Nova market identifier. |
| `market_name` | Nova market city name. |
| `region` | Nova market region. |
| `category` | Service category. |
| `active_services` | Count of services in the market/category. |
| `avg_service_rating` | Average service rating. |
| `avg_popularity_score` | Average service popularity score. |
| `head_services` | Number of head-tier services. |
| `mid_services` | Number of mid-tier services. |
| `long_tail_services` | Number of long-tail services. |
| `*_service_share` fields | Service tier share by market/category. |

**Preview (selected columns, 5 rows):**

| market_id | market_name | category | active_services | avg_service_rating | head_services | mid_services | long_tail_services | head_service_share | long_tail_service_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Singapore | Digital Wallet | 431 | 4.3696 | 9 | 80 | 342 | 0.0209 | 0.7935 |
| 1 | Singapore | E-Commerce | 714 | 4.3978 | 11 | 138 | 565 | 0.0154 | 0.7913 |
| 1 | Singapore | Food Delivery | 1087 | 4.3929 | 25 | 198 | 864 | 0.0230 | 0.7948 |
| 1 | Singapore | Grocery | 538 | 4.3968 | 11 | 98 | 429 | 0.0204 | 0.7974 |
| 1 | Singapore | Ride Hailing | 761 | 4.3792 | 12 | 128 | 621 | 0.0158 | 0.8160 |

**Tests:** not-null grain and core supply fields; relationship to `stg_markets`; no duplicate grain rows.
