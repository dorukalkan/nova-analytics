---
icon: lucide/house
title: Overview
description: End-to-end Nova analytics portfolio project overview
---

<p class="landing-page-banner">
  <img src="assets/nova_banner.png" alt="Nova Analytics project banner">
</p>

# Nova Analytics Project

Nova Analytics is an end-to-end analytics portfolio project built around a global super-app marketplace dataset. We regenerated the dataset for realism, loaded it into BigQuery, wrote SQL queries and dbt models from staging to marts, used Python/Jupyter for modeling and anomaly analysis, and published the findings through Tableau dashboards and this Zensical writeup site.

!!! abstract "Quick summary"

    This project demonstrates SQL querying, dbt modeling, BigQuery warehousing, Python analysis, Tableau dashboarding, and business storytelling in one tested analytics pipeline. The analysis connects marketplace scale, demand drivers, category performance, customer value, repeat behavior, and transaction risk to practical recommendations.

## Project at a Glance

| Area | Summary |
| --- | --- |
| Dataset scale | **50M interactions**, **1.71M active users**, **50K services** |
| Marketplace value | **$2.66B GMV** across 2024 |
| Coverage | **16 city markets** across **4 continents** and **8 regions** |
| Analysis output | **7 Tableau-backed analysis pages** |
| Pipeline | regenerated dataset, BigQuery, SQL, dbt staging/intermediate/marts, Python notebooks, Tableau |

## Analysis Portfolio

Each analysis page focuses on a business question and connects the Tableau dashboard to the underlying data pipeline.

<div class="grid cards" markdown>

-   :lucide-layout-dashboard:{ .lg .middle } __[Executive Summary](analyses/executive_summary.md)__

    ---

    Marketplace scale, headline GMV, customer base shape, and the overall analytics pipeline.

    _Author: Doruk Alkan_

-   :lucide-map:{ .lg .middle } __[Marketplace Analysis](analyses/marketplace_analysis.md)__

    ---

    Regional performance, market opportunity scoring, and growth prioritization across 16 markets.

    _Author: Doruk Alkan_

-   :lucide-cloud-sun:{ .lg .middle } __[Local Demand Drivers](analyses/demand_drivers.md)__

    ---

    Weather effects, service supply, timing patterns, demand modeling, and market profiles.

    _Author: Doruk Alkan_

-   :lucide-chart-bar:{ .lg .middle } __[Category Performance](analyses/category_performance.md)__

    ---

    Category GMV, service reliability, operational risk, and where category growth needs stabilization.

    _Author: Yasemen Nur Salım Dündar_

-   :lucide-shield-alert:{ .lg .middle } __[Customer Repeat & Risk](analyses/customer_risk.md)__

    ---

    Repeat behavior, suspicious transaction patterns, anomaly scoring, and risk-review priorities.

    _Author: Yasemen Nur Salım Dündar_

-   :lucide-user-round-check:{ .lg .middle } __[Customer Analysis](analyses/customer_analysis.md)__

    ---

    Membership tiers, acquisition channels, lifecycle behavior, and customer value concentration.

    _Author: Merve Kaymaz_

-   :lucide-repeat:{ .lg .middle } __[RFM Analysis](analyses/rfm_analysis.md)__

    ---

    Recency, frequency, monetary segmentation, retention priorities, and customer development opportunities.

    _Author: Merve Kaymaz_

</div>

## dbt Models

<div class="grid cards" markdown>

-   :lucide-sprout:{ .lg .middle } __[dbt Seeds](models/seeds.md)__

    ---

    External enrichment inputs used for geography, weather, and macro context.

-   :lucide-arrows-up-from-line:{ .lg .middle } __[Staging Models](models/staging.md)__

    ---

    Clean source interfaces for transactions, users, services, markets, and external context.

-   :lucide-package-open:{ .lg .middle } __[Intermediate Models](models/intermediate.md)__

    ---

    Reusable SQL business logic for demand, service health, customer behavior, and RFM scoring.

-   :lucide-package-search:{ .lg .middle } __[Analytics Marts](models/marts.md)__

    ---

    Final Tableau and notebook-facing models used by the analysis pages.

</div>

## Further Info

<div class="grid cards" markdown>

-   :lucide-database:{ .lg .middle } __[Dataset](about/dataset.md)__

    ---

    Source dataset, regeneration rationale, corrected data scope, and what the project contains.

-   :lucide-cloud-download:{ .lg .middle } __[API Sources](about/api_sources.md)__

    ---

    External weather, country metadata, and macroeconomic sources used for enrichment.

-   :lucide-users:{ .lg .middle } __[Team](about/team.md)__

    ---

    Contributor ownership across analysis, modeling, dashboards, and writeups.

-   :fontawesome-brands-github:{ .lg .middle } __[GitHub Repository](https://github.com/mmervekaymaz/nova-analytics)__

    ---

    Source code, SQL queries, dbt models, notebooks, dashboards, and site files.

</div>
