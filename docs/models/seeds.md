---
icon: lucide/sprout
title: dbt Seeds
description: External enrichment data used by the Nova analytics pipeline
---

# dbt Seeds

Seeds are the external context layer of the Nova project. They do not describe Nova transactions directly; they make the marketplace analyses richer by connecting city markets to countries, weather, and macroeconomic signals.

In the pipeline, these files are loaded with `dbt seed`, staged with `stg_geo_*` models, and then joined into intermediate and mart models for marketplace and demand analysis.

The seed files were generated from external APIs and reviewed lookup logic using Python fetch scripts. For source details and API references, see [API Sources](../about/api_sources.md).

!!! abstract "Layer purpose"

    The seed layer answers: what external context do we need before Nova's internal marketplace data can be compared across cities, countries, weather patterns, and growth opportunities?

## Seed Inputs

| Seed | What it adds | Used for |
| --- | --- | --- |
| `market_country_lookup` | Reviewed mapping from each Nova city market to country identifiers | Marketplace analysis, market opportunity scoring, geo joins |
| `ext_weather_daily` | Daily 2024 Open-Meteo weather by Nova market | Demand drivers, weather sensitivity, hourly/category demand interpretation |
| `ext_world_bank_indicators` | Country-level macro indicators such as population, GDP per capita, urbanization, internet usage, and mobile subscriptions | Market opportunity scoring and country context |
| `ext_country_metadata` | REST Countries metadata such as region, currency, capital, and timezone | Market labeling, country context, geography enrichment |

## Why This Matters

Nova's raw platform data can show where transactions happened, but it cannot explain the local context on its own. The seed layer lets the project ask broader business questions:

- which markets have strong current usage but lower macro headroom;
- whether demand behaves differently under local weather conditions;
- how market opportunity changes when service supply, adoption, and country context are considered together;
- whether geographic analysis should be grouped by city, country, region, or macro profile.

## Analysis Coverage

| Analysis page | Seed contribution |
| --- | --- |
| Marketplace Analysis | Country mapping, macro indicators, and market context support opportunity scoring |
| Local Demand Drivers | Weather seeds support bad-weather lift, rain sensitivity, and demand feature engineering |
| Executive Summary | External context helps explain why growth is concentrated in specific markets |
