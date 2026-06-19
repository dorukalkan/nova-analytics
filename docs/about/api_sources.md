---
icon: lucide/cloud-download
title: API Sources
description: External API sources used for geography and market opportunity analysis
---

# API Sources

We used external APIs to enrich the Nova transaction data with market geography, historical weather, country metadata, and macroeconomic context. These sources help turn a transaction dataset into a market opportunity analysis: not just where activity happened, but which markets have stronger demand signals, operating conditions, and growth context.

## Sources Used

| Source | API docs | How we used it |
| --- | --- | --- |
| [Open-Meteo](https://open-meteo.com/) | [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) | Added daily market-level weather signals such as temperature, precipitation, rain, weather code, and wind speed. Open-Meteo documents this API as reanalysis-based historical weather data from model sources including ERA5, ERA5-Land, and ECMWF IFS. |
| [World Bank Open Data](https://data.worldbank.org/) | [Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation) | Added country-level macro indicators such as population, GDP per capita, urbanization, internet usage, and mobile subscriptions. World Bank datasets are published under open data licensing, with attribution expected for reused data. |
| [REST Countries](https://restcountries.com/)[^1] | [REST Countries docs](https://restcountries.com/docs) | Added country metadata such as ISO codes, region, subregion, capital, currency, population, and time zones. REST Countries compiles country fields from public registries, multilateral bodies, and open-data projects. |

These APIs are used for analytical enrichment only. The final market opportunity analysis should still cite the source page relevant to any external metric shown in a report or dashboard.

[^1]: REST Countries requires an API key for full access. Open-Meteo and the World Bank Indicators API did not require API keys for the calls used in this project.
