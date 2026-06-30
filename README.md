<p align="center">
  <img src="docs/assets/nova_banner.png" alt="Nova Analytics banner">
</p>

# Nova Analytics

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-Analytics_Engineering-FF694B?logo=dbt&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-Cloud_Warehouse-4285F4?logo=googlecloud&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-BI_Dashboards-E97627?logo=tableau&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-F37626?logo=jupyter&logoColor=white)

Nova Analytics is an end-to-end analytics portfolio project built around a global super-app marketplace dataset. The project covers realistic data regeneration, BigQuery warehousing, dbt modeling, Python analysis, Tableau dashboards, and a Zensical writeup site for business storytelling.

**Full project site:** https://nova-analytics-project.vercel.app. Site source starts at [docs/index.md](docs/index.md).

## Project Snapshot

| Area | Summary |
| --- | --- |
| Dataset scale | 50M interactions, 1.71M active users, 50K services |
| Marketplace value | $2.66B GMV across 2024 |
| Coverage | 16 city markets across 4 continents and 8 regions |
| Analysis output | 7 Tableau-backed analysis pages |
| Pipeline | Regenerated dataset, BigQuery, SQL, dbt staging/intermediate/marts, Python notebooks, Tableau |

## What This Demonstrates

- Analytics engineering with tested dbt staging, intermediate, mart, and ML feature layers.
- Cloud warehouse modeling for marketplace, customer, service, category, geography, and risk analysis.
- 50M-row synthetic data correction with QA checks for grain, relationships, realism, and BigQuery readiness.
- External enrichment from weather, country metadata, and macroeconomic APIs.
- Python modeling for local demand drivers, market clustering, and unsupervised transaction anomaly detection.
- Recruiter-friendly business storytelling through Tableau dashboards and a bilingual documentation site.

## Analysis Areas

| Analysis | Business focus |
| --- | --- |
| Executive Summary | Marketplace scale, headline GMV, customer base shape, and pipeline overview |
| Marketplace Analysis | Regional performance, market opportunity scoring, and growth prioritization |
| Local Demand Drivers | Weather effects, service supply, timing patterns, and demand modeling |
| Category Performance | Category GMV, service reliability, operational risk, and growth stabilization |
| Customer Repeat & Risk | Repeat behavior, suspicious transaction patterns, anomaly scoring, and review priorities |
| Customer Analysis | Membership tiers, acquisition channels, lifecycle behavior, and value concentration |
| RFM Analysis | Recency, frequency, monetary segmentation, retention priorities, and customer development |

## Repository Structure

```text
.
|-- nova/                 # dbt project: sources, staging, intermediate, marts, tests, seeds
|-- scripts/              # data regeneration, validation, and external seed fetchers
|-- notebooks/            # EDA, fraud detection, demand modeling, and clustering notebooks
|-- docs/                 # English Zensical project site content
|-- docs-tr/              # Turkish Zensical project site content
|-- docs/assets/          # banner, logos, dashboard images, icons
|-- exports/              # exported analysis visuals
|-- config/               # synthetic data correction configuration
`-- vercel.json           # documentation site deployment build config
```

## Data & Modeling Notes

The project starts from the public [Nova 50M Transactions Super-App dataset](https://www.kaggle.com/datasets/adityathakekar/nova-50m-transactions-super-app), a synthetic marketplace dataset with interactions, users, services, and markets.

We regenerated the dataset before modeling so the final analytics layer had more realistic behavior: market-level seasonality, category-specific basket sizes, service supply effects, customer lifecycle variation, weather sensitivity, and fraud-like transaction patterns.

The dbt models and notebooks were designed around a private BigQuery project, so this repository intentionally does not include public run instructions or warehouse credentials. The code, model structure, notebooks, and documentation remain available for review.

Fraud analysis is unsupervised anomaly detection. Suspicious transaction flags are meant for review workflows and should not be interpreted as confirmed fraud labels.

## Team

| Contributor | Focus |
| --- | --- |
| Doruk Alkan | Market opportunity, external API enrichment, demand modeling, market clustering, Tableau, and project site |
| Yasemen Salım Dundar | Category and service performance, repeat customer and risk behavior, fraud anomaly analysis, and Tableau |
| Merve Kaymaz | Customer lifecycle, acquisition analysis, customer value segmentation, RFM analysis, and Tableau |

Full contributor details are available in [docs/about/team.md](docs/about/team.md).
