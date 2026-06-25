---
icon: lucide/database
title: Dataset
description: Source dataset and correction approach for the Nova analytics project
---

# Dataset

This project starts from the public [Nova 50M Transactions Super-App dataset](https://www.kaggle.com/datasets/adityathakekar/nova-50m-transactions-super-app), a synthetic marketplace dataset representing transactions, users, services, and operating markets for a global super-app.

## What It Contains

The source data includes four core entities:

| Entity | What it represents | Example fields |
| --- | --- | --- |
| Interactions | Transaction-level marketplace activity | User, service, category, amount, status, timestamp, platform, referral source, location |
| Users | Customer profile attributes | Membership tier, device, acquisition source, market |
| Services | Service and category metadata | Category, rating, marketplace availability |
| Markets | City-level operating markets | Market name, region, latitude, longitude |

## How We Used It

We treated the original dataset as a starting point, then regenerated the dataset for realism before building the final analytics layer.

The regeneration step preserved the project scale and core schema, but added more realistic business behavior: market-level seasonality, category-specific demand and basket sizes, weather sensitivity, service supply effects, customer lifecycle variation, and fraud-like transaction patterns.

The dashboards and dbt models in this project use the regenerated dataset, not the raw Kaggle files directly.
