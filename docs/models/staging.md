---
icon: lucide/arrows-up-from-line
title: Staging Models
description: dbt staging models documentation
---

# Staging Models

This page documents the geography-track staging models. Staging models are thin, analysis-safe interfaces over raw sources or seeds: they standardize names, preserve source grain, and avoid business scoring logic.

## Geography Seed Staging

All `stg_geo_*` models are views in the active dbt target dataset. They currently build in:

```text
nova-project-498911.dbt_doruk
```

### stg_geo_market_country_lookup

Staging model for the reviewed Nova market-to-country lookup seed.

**Grain:** one row per Nova market.

**Keys and joins:**

- Primary key: `market_id`
- Join to Nova market models on `market_id`
- Join to country-level geography models on `country_iso3`

| Column | Description |
| --- | --- |
| `market_id` | Nova market identifier. |
| `market_name` | Nova market city name. |
| `country_name` | Reviewed country name for the market. |
| `country_iso2` | ISO 3166-1 alpha-2 country code. |
| `country_iso3` | ISO 3166-1 alpha-3 country code. |
| `world_bank_country_code` | Lowercase country code used in World Bank API calls. |
| `seed_source` | Seed source label. |
| `seed_fetched_at` | Timestamp when the seed was generated. |

**Preview (5 rows):**

| market_id | market_name | country_name | country_iso2 | country_iso3 | world_bank_country_code | seed_source | seed_fetched_at |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Singapore | Singapore | SG | SGP | sgp | manual_reviewed_lookup | 2026-06-11 10:40:28+00 |
| 2 | Jakarta | Indonesia | ID | IDN | idn | manual_reviewed_lookup | 2026-06-11 10:40:28+00 |
| 3 | Manila | Philippines | PH | PHL | phl | manual_reviewed_lookup | 2026-06-11 10:40:28+00 |
| 4 | Bangkok | Thailand | TH | THA | tha | manual_reviewed_lookup | 2026-06-11 10:40:28+00 |
| 5 | Ho Chi Minh City | Vietnam | VN | VNM | vnm | manual_reviewed_lookup | 2026-06-11 10:40:28+00 |

**Tests:** unique and not-null `market_id`; not-null country fields.

### stg_geo_weather_daily

Staging model for daily Open-Meteo weather by Nova market.

**Grain:** one row per market per weather date.

**Keys and joins:**

- Primary key: `market_id`, `weather_date`
- Join to `stg_geo_market_country_lookup` on `market_id`
- Join to future market-day marts on `market_id` and date

| Column | Description |
| --- | --- |
| `market_id` | Nova market identifier. |
| `market_name` | Nova market city name. |
| `weather_date` | Local weather date. |
| `weather_code` | Open-Meteo weather condition code. |
| `temperature_2m_mean_c` | Daily mean temperature in Celsius. |
| `temperature_2m_max_c` | Daily maximum temperature in Celsius. |
| `temperature_2m_min_c` | Daily minimum temperature in Celsius. |
| `apparent_temperature_mean_c` | Daily mean apparent temperature in Celsius. |
| `precipitation_sum_mm` | Daily total precipitation in millimeters. |
| `rain_sum_mm` | Daily total rain in millimeters. |
| `precipitation_hours` | Number of hours with precipitation. |
| `wind_speed_10m_max_kmh` | Daily maximum wind speed at 10 meters in km/h. |
| `is_rain_day` | True when rain or precipitation is greater than zero. |
| `seed_source` | Seed source label. |
| `seed_fetched_at` | Timestamp when the seed was generated. |

**Preview (selected columns, 5 rows):**

| market_id | market_name | weather_date | weather_code | temperature_2m_mean_c | precipitation_sum_mm | rain_sum_mm | is_rain_day | wind_speed_10m_max_kmh | seed_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Singapore | 2024-01-01 | 63 | 25.5 | 12.5 | 12.5 | true | 14.7 | open_meteo_historical_weather_api |
| 1 | Singapore | 2024-01-02 | 63 | 25.9 | 25.8 | 25.8 | true | 15.8 | open_meteo_historical_weather_api |
| 1 | Singapore | 2024-01-03 | 65 | 25.7 | 25.6 | 25.6 | true | 13.3 | open_meteo_historical_weather_api |
| 1 | Singapore | 2024-01-04 | 63 | 24.9 | 16.2 | 16.2 | true | 16.0 | open_meteo_historical_weather_api |
| 1 | Singapore | 2024-01-05 | 63 | 25.3 | 19.2 | 19.2 | true | 19.7 | open_meteo_historical_weather_api |

**Tests:** not-null key/weather fields; relationship to market lookup; no duplicate `market_id + weather_date`.

### stg_geo_world_bank_indicators

Staging model for long-form World Bank macro indicators.

**Grain:** one row per country per World Bank indicator.

**Keys and joins:**

- Primary key: `country_iso3`, `indicator_code`
- Join to `stg_geo_market_country_lookup` on `country_iso3`
- Pivot in intermediate models before joining to market-level tables

| Column | Description |
| --- | --- |
| `country_iso3` | ISO 3166-1 alpha-3 country code. |
| `country_name` | World Bank country name. |
| `indicator_code` | World Bank indicator code. |
| `metric_name` | Project-friendly metric name. |
| `indicator_name` | World Bank indicator name. |
| `indicator_year` | Latest available year returned for the indicator. |
| `indicator_value` | Indicator value. |
| `seed_source` | Seed source label. |
| `seed_fetched_at` | Timestamp when the seed was generated. |

**Preview (selected columns, 5 rows):**

| country_iso3 | country_name | indicator_code | metric_name | indicator_year | indicator_value | seed_source |
| --- | --- | --- | --- | --- | --- | --- |
| ARE | United Arab Emirates | IT.CEL.SETS.P2 | mobile_subscriptions_per_100_people | 2024 | 203.2064 | world_bank_api |
| ARE | United Arab Emirates | IT.NET.USER.ZS | internet_users_pct | 2024 | 100.0000 | world_bank_api |
| ARE | United Arab Emirates | NY.GDP.PCAP.CD | gdp_per_capita_current_usd | 2024 | 50273.5060 | world_bank_api |
| ARE | United Arab Emirates | SP.POP.TOTL | population_total | 2024 | 10986400 | world_bank_api |
| ARE | United Arab Emirates | SP.URB.TOTL.IN.ZS | urban_population_pct | 2024 | 85.8171 | world_bank_api |

**Tests:** not-null key/value fields; accepted indicator codes; relationship to market lookup; no duplicate `country_iso3 + indicator_code`.

### stg_geo_country_metadata

Staging model for REST Countries metadata.

**Grain:** one row per country.

**Keys and joins:**

- Primary key: `country_iso3`
- Join to `stg_geo_market_country_lookup` on `country_iso3`
- Join to pivoted World Bank macro context on `country_iso3`

| Column | Description |
| --- | --- |
| `country_iso3` | ISO 3166-1 alpha-3 country code. |
| `country_iso2` | ISO 3166-1 alpha-2 country code. |
| `country_name_common` | Common country name. |
| `country_name_official` | Official country name. |
| `region` | REST Countries region. |
| `subregion` | REST Countries subregion. |
| `capital` | Country capital. |
| `currency_code` | Primary currency code. |
| `currency_name` | Primary currency name. |
| `currency_symbol` | Primary currency symbol. |
| `population` | REST Countries population value. |
| `timezones` | Pipe-delimited timezone list. |
| `seed_source` | Seed source label. |
| `seed_fetched_at` | Timestamp when the seed was generated. |

**Preview (selected columns, 5 rows):**

| country_iso3 | country_iso2 | country_name_common | region | subregion | capital | currency_code | population | seed_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARE | AE | United Arab Emirates | Asia | Western Asia | Abu Dhabi | AED | 11027129 | rest_countries_api |
| AUS | AU | Australia | Oceania | Australia and New Zealand | Canberra | AUD | 27724744 | rest_countries_api |
| BRA | BR | Brazil | Americas | South America | Brasilia | BRL | 213421037 | rest_countries_api |
| GBR | GB | United Kingdom | Europe | Northern Europe | London | GBP | 66912637 | rest_countries_api |
| IDN | ID | Indonesia | Asia | South-Eastern Asia | Jakarta | IDR | 288315089 | rest_countries_api |

**Tests:** unique and not-null `country_iso3`; not-null country and currency fields; relationship to market lookup.
