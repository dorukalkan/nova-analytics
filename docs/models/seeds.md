---
icon: lucide/sprout
title: dbt Seeds
description: dbt seeds fetched from multiple API sources
---

# dbt Seeds

These seed tables store external geography context used by the Nova market opportunity and local demand driver analysis. They are generated as CSV files under `nova/seeds/` and loaded to BigQuery with `dbt seed`.

In development, seeds build into the active developer dataset from the local dbt profile. For this workspace that is currently:

```text
nova-project-498911.dbt_doruk
```

## market_country_lookup

Reviewed lookup that maps each Nova city market to a country identifier. This table is the bridge between Nova market-level data and country-level external sources.

**Grain:** one row per Nova market.

**Keys and joins:**

- Primary key: `market_id`
- Join to Nova market models on `market_id`
- Join to country-level external seeds on `country_iso3`

| Column | Type | Description |
| --- | --- | --- |
| `market_id` | `INT64` | Nova market identifier. |
| `market_name` | `STRING` | Nova market city name. |
| `country_name` | `STRING` | Reviewed country name for the market. |
| `country_iso2` | `STRING` | ISO 3166-1 alpha-2 country code. |
| `country_iso3` | `STRING` | ISO 3166-1 alpha-3 country code. |
| `world_bank_country_code` | `STRING` | Lowercase country code used in World Bank API calls. |
| `source` | `STRING` | Seed source label. |
| `fetched_at_utc` | `TIMESTAMP` | Timestamp when the seed was generated. |

**Preview**

| market_id | market_name | country_name | country_iso2 | country_iso3 | world_bank_country_code | source | fetched_at_utc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Singapore | Singapore | SG | SGP | sgp | manual_reviewed_lookup | 2026-06-11T10:40:28Z |
| 2 | Jakarta | Indonesia | ID | IDN | idn | manual_reviewed_lookup | 2026-06-11T10:40:28Z |
| 3 | Manila | Philippines | PH | PHL | phl | manual_reviewed_lookup | 2026-06-11T10:40:28Z |
| 4 | Bangkok | Thailand | TH | THA | tha | manual_reviewed_lookup | 2026-06-11T10:40:28Z |
| 5 | Ho Chi Minh City | Vietnam | VN | VNM | vnm | manual_reviewed_lookup | 2026-06-11T10:40:28Z |

## ext_weather_daily

Daily historical weather by Nova market from Open-Meteo. This is the main external source for local daily demand modeling.

**Grain:** one row per market per calendar date.

**Keys and joins:**

- Primary key: `market_id`, `weather_date`
- Join to `market_country_lookup` on `market_id`
- Join to market-day or market-category-day marts on `market_id` and date

| Column | Type | Description |
| --- | --- | --- |
| `market_id` | `INT64` | Nova market identifier. |
| `market_name` | `STRING` | Nova market city name. |
| `weather_date` | `DATE` | Local weather date. |
| `weather_code` | `INT64` | Open-Meteo weather condition code. |
| `temperature_2m_mean_c` | `FLOAT64` | Daily mean temperature in Celsius. |
| `temperature_2m_max_c` | `FLOAT64` | Daily maximum temperature in Celsius. |
| `temperature_2m_min_c` | `FLOAT64` | Daily minimum temperature in Celsius. |
| `apparent_temperature_mean_c` | `FLOAT64` | Daily mean apparent temperature in Celsius. |
| `precipitation_sum_mm` | `FLOAT64` | Daily total precipitation in millimeters. |
| `rain_sum_mm` | `FLOAT64` | Daily total rain in millimeters. |
| `precipitation_hours` | `FLOAT64` | Number of hours with precipitation. |
| `wind_speed_10m_max_kmh` | `FLOAT64` | Daily maximum wind speed at 10 meters in km/h. |
| `is_rain_day` | `BOOL` | True when rain or precipitation is greater than zero. |
| `source` | `STRING` | Seed source label. |
| `fetched_at_utc` | `TIMESTAMP` | Timestamp when the seed was generated. |

**Preview**

| market_id | market_name | weather_date | weather_code | temperature_2m_mean_c | temperature_2m_max_c | temperature_2m_min_c | apparent_temperature_mean_c | precipitation_sum_mm | rain_sum_mm | precipitation_hours | wind_speed_10m_max_kmh | is_rain_day | source | fetched_at_utc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Singapore | 2024-01-01 | 63 | 25.5 | 29.0 | 23.1 | 30.5 | 12.5 | 12.5 | 13.0 | 14.7 | True | open_meteo_historical_weather_api | 2026-06-11T10:40:28Z |
| 1 | Singapore | 2024-01-02 | 63 | 25.9 | 29.8 | 23.3 | 30.9 | 25.8 | 25.8 | 13.0 | 15.8 | True | open_meteo_historical_weather_api | 2026-06-11T10:40:28Z |
| 1 | Singapore | 2024-01-03 | 65 | 25.7 | 29.5 | 23.4 | 30.8 | 25.6 | 25.6 | 10.0 | 13.3 | True | open_meteo_historical_weather_api | 2026-06-11T10:40:28Z |
| 1 | Singapore | 2024-01-04 | 63 | 24.9 | 27.5 | 23.2 | 29.5 | 16.2 | 16.2 | 15.0 | 16.0 | True | open_meteo_historical_weather_api | 2026-06-11T10:40:28Z |
| 1 | Singapore | 2024-01-05 | 63 | 25.3 | 28.4 | 23.4 | 29.5 | 19.2 | 19.2 | 14.0 | 19.7 | True | open_meteo_historical_weather_api | 2026-06-11T10:40:28Z |

## ext_world_bank_indicators

Country-level macro indicators from the World Bank. These fields support market opportunity scoring and country context.

**Grain:** one row per country per indicator.

**Keys and joins:**

- Primary key: `country_iso3`, `indicator_code`
- Join to `market_country_lookup` on `country_iso3`
- Usually pivot or aggregate in an intermediate model before joining to market-level marts

| Column | Type | Description |
| --- | --- | --- |
| `country_iso3` | `STRING` | ISO 3166-1 alpha-3 country code. |
| `country_name` | `STRING` | World Bank country name. |
| `indicator_code` | `STRING` | World Bank indicator code. |
| `metric_name` | `STRING` | Project-friendly metric name. |
| `indicator_name` | `STRING` | World Bank indicator name. |
| `indicator_year` | `INT64` | Latest available year returned for the indicator. |
| `indicator_value` | `FLOAT64` | Indicator value. |
| `source` | `STRING` | Seed source label. |
| `fetched_at_utc` | `TIMESTAMP` | Timestamp when the seed was generated. |

**Preview**

| country_iso3 | country_name | indicator_code | metric_name | indicator_name | indicator_year | indicator_value | source | fetched_at_utc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARE | United Arab Emirates | IT.CEL.SETS.P2 | mobile_subscriptions_per_100_people | Mobile cellular subscriptions (per 100 people) | 2024 | 203.206410299544 | world_bank_api | 2026-06-11T10:40:28Z |
| ARE | United Arab Emirates | IT.NET.USER.ZS | internet_users_pct | Individuals using the Internet (% of population) | 2024 | 100 | world_bank_api | 2026-06-11T10:40:28Z |
| ARE | United Arab Emirates | NY.GDP.PCAP.CD | gdp_per_capita_current_usd | GDP per capita (current US$) | 2024 | 50273.5060469837 | world_bank_api | 2026-06-11T10:40:28Z |
| ARE | United Arab Emirates | SP.POP.TOTL | population_total | Population, total | 2024 | 10986400 | world_bank_api | 2026-06-11T10:40:28Z |
| ARE | United Arab Emirates | SP.URB.TOTL.IN.ZS | urban_population_pct | Urban population (% of total population) | 2024 | 85.8171088279791 | world_bank_api | 2026-06-11T10:40:28Z |

## ext_country_metadata

Country metadata from REST Countries. This seed adds currency, region, subregion, capital, population, and timezone context for market documentation and Power BI labels.

**Grain:** one row per country.

**Keys and joins:**

- Primary key: `country_iso3`
- Join to `market_country_lookup` on `country_iso3`
- Join to pivoted World Bank indicators on `country_iso3`

| Column | Type | Description |
| --- | --- | --- |
| `country_iso3` | `STRING` | ISO 3166-1 alpha-3 country code. |
| `country_iso2` | `STRING` | ISO 3166-1 alpha-2 country code. |
| `country_name_common` | `STRING` | Common country name. |
| `country_name_official` | `STRING` | Official country name. |
| `region` | `STRING` | REST Countries region. |
| `subregion` | `STRING` | REST Countries subregion. |
| `capital` | `STRING` | Country capital. |
| `currency_code` | `STRING` | Primary currency code. |
| `currency_name` | `STRING` | Primary currency name. |
| `currency_symbol` | `STRING` | Primary currency symbol. |
| `population` | `INT64` | REST Countries population value. |
| `timezones` | `STRING` | Pipe-delimited timezone list. |
| `source` | `STRING` | Seed source label. |
| `fetched_at_utc` | `TIMESTAMP` | Timestamp when the seed was generated. |

**Preview**

| country_iso3 | country_iso2 | country_name_common | country_name_official | region | subregion | capital | currency_code | currency_name | currency_symbol | population | timezones | source | fetched_at_utc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARE | AE | United Arab Emirates | United Arab Emirates | Asia | Western Asia | Abu Dhabi | AED | United Arab Emirates dirham | د.إ | 11027129 | UTC+04:00 | rest_countries_api | 2026-06-11T10:49:02Z |
| AUS | AU | Australia | Commonwealth of Australia | Oceania | Australia and New Zealand | Canberra | AUD | Australian dollar | $ | 27724744 | UTC+05:00\|UTC+06:30\|UTC+07:00\|UTC+08:00\|UTC+09:30\|UTC+10:00\|UTC+10:30\|UTC+11:30 | rest_countries_api | 2026-06-11T10:49:02Z |
| BRA | BR | Brazil | Federative Republic of Brazil | Americas | South America | Brasília | BRL | Brazilian real | R$ | 213421037 | UTC-05:00\|UTC-04:00\|UTC-03:00\|UTC-02:00 | rest_countries_api | 2026-06-11T10:49:02Z |
| GBR | GB | United Kingdom | United Kingdom of Great Britain and Northern Ireland | Europe | Northern Europe | London | GBP | British pound | £ | 66912637 | UTC-08:00\|UTC-05:00\|UTC-04:00\|UTC-03:00\|UTC-02:00\|UTC\|UTC+01:00\|UTC+02:00\|UTC+06:00 | rest_countries_api | 2026-06-11T10:49:02Z |
| IDN | ID | Indonesia | Republic of Indonesia | Asia | South-Eastern Asia | Jakarta | IDR | Indonesian rupiah | Rp | 288315089 | UTC+07:00\|UTC+08:00\|UTC+09:00 | rest_countries_api | 2026-06-11T10:49:02Z |
