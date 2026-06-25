---
icon: lucide/package-search
title: Analytics Marts
description: Analysis-ready dbt marts and ML feature outputs
---

# Analytics-Ready Marts

Marts are the final dbt contracts used by Tableau dashboards, notebooks, and the project writeups. They are intentionally closer to business questions than raw data: market opportunity, demand drivers, category health, customer segments, repeat behavior, and transaction anomaly review.

!!! abstract "Layer purpose"

    The mart layer answers: what clean, analysis-ready tables should Tableau and modeling notebooks consume?

## Marketplace Growth

| Mart | What it provides | Analysis output |
| --- | --- | --- |
| `mart_geo_market_opportunity` | Market-level performance, growth, supply, macro, adoption, reliability, and opportunity scoring | Marketplace Analysis |

This mart supports the market opportunity story by combining current Nova performance with external country context and supply signals. It is where the project moves from "which markets are large?" to "which markets are attractive growth candidates?"

## Demand Drivers and Modeling

| Mart | What it provides | Analysis output |
| --- | --- | --- |
| `mart_geo_market_category_day_features` | Market-category-day feature table with demand, weather, calendar, macro, supply, and service signals | Demand modeling notebook, Local Demand Drivers |
| `mart_geo_weather_category_effects` | Bad-weather transaction and GMV lift by category and market | Local Demand Drivers |
| `mart_geo_weather_category_sensitivity` | Rain sensitivity and weather-correlation summary | Local Demand Drivers, market clustering |
| `mart_geo_category_hourly_demand` | Hourly demand curves by market and category | Local Demand Drivers |
| `mart_geo_market_cluster_features` | Market-level feature table for strategic clustering | Local Demand Drivers |

These marts support the demand-driver narrative: weather matters in some categories, but service supply and market context explain more of the demand picture.

## Category and Service Performance

| Mart | What it provides | Analysis output |
| --- | --- | --- |
| `mart_category_performance` | Category-level GMV, amount share, success, failure, refund, rating, and risk-segment counts | Category Performance |
| `mart_category_market_performance` | Category performance split by market | Category Performance |
| `mart_marketplace_service` | Service-level amount, reliability, rank, and risk segment | Category Performance |
| `mart_service_monthly_performance` | Monthly service-health tracking | Category and service monitoring |

These marts make category performance operational. They show not only which categories are large, but also where reliability leakage, refunds, failures, and critical services need attention.

## Customer Segmentation

| Mart | What it provides | Analysis output |
| --- | --- | --- |
| `mart_customer_overview` | Customer profile, membership, acquisition, lifecycle, transaction count, completed revenue, average order value, and recency fields | Customer Analysis |
| `mart_customer_segments` | RFM scores and business-friendly segments such as Champions, Loyal Customers, Potential Loyalists, At Risk, and Lost Customers | RFM Analysis |

These marts support the customer strategy pages. They separate user count from customer value, showing which groups are worth retaining, upgrading, or reactivating.

## Repeat and Risk Analytics

| Artifact | What it provides | Analysis output |
| --- | --- | --- |
| `mart_service_repeat_behavior` | Repeat users, repeat interactions, repeat amount, and repeat dependency by service/category | Customer Repeat & Risk |
| `ml_transaction_fraud_features` | Transaction-level behavioral features for anomaly detection | Fraud anomaly notebook |
| `ml_transaction_fraud_scores_sample` | Isolation Forest anomaly scores written from the notebook | Customer Repeat & Risk |
| `mart_transaction_fraud_tableau` | Tableau-ready transaction context joined to anomaly scores and suspicious flags | Customer Repeat & Risk |

The risk workflow combines dbt and notebook modeling. dbt builds the transaction-level feature table, the notebook scores anomalies, and the final mart joins those scores back to business context for review.

!!! warning "Fraud interpretation"

    The fraud workflow is unsupervised anomaly detection. The output flags suspicious transactions for review; it does not prove confirmed fraud.

## Quality Controls

Mart tests check unique business grains, required metrics, accepted customer segment labels, and core anomaly-score fields. Custom dbt tests also validate geography grains and reconciliation between market-day, category-day, and feature-mart totals.

!!! success "Why this matters"

    The marts are the bridge between engineering and storytelling. They make the Tableau dashboards and project writeups credible because the business metrics come from tested, reusable models rather than one-off dashboard calculations.
