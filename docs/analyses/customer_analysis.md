---
icon: lucide/user-round-check
title: Customer Analysis
description: Customer segmentation and lifecycle behavior dashboard
author: Merve Kaymaz
---

# Customer Analysis

=== "Insights"

    ![Tableau Customer Analysis Dashboard](../assets/6_customer_analysis.jpeg)

    Customer Analysis profiles Nova's customer base by membership tier, acquisition source, lifecycle stage, and revenue contribution. It shows who the customers are, how valuable different groups are, and where growth or retention work should focus.

    !!! abstract "What this page answers"

        - Which customer groups contribute the most revenue?
        - How does revenue vary across membership tiers?
        - Which acquisition sources bring the most users and revenue?
        - How are customers distributed across lifecycle stages?

    ## KPI Cards

    | KPI | What it shows | Why it matters |
    | --- | --- | --- |
    | Premium Members | Share of customers in Gold or Platinum membership tiers | Shows the size of the high-value customer base |
    | Organic Search Share | Share of customers acquired through organic search | Indicates how much growth comes from unpaid discovery |
    | Top Revenue Segment | Lifecycle or customer segment with the highest revenue | Identifies the group most responsible for current business value |

    ## Dashboard Views

    | View | What it shows | Business use |
    | --- | --- | --- |
    | Membership Distribution | Standard, Gold, and Platinum customer mix | Shows room for premium tier growth |
    | Revenue per Customer by Tier | Average revenue by membership tier | Validates whether premium tiers behave as higher-value groups |
    | Acquisition Source Analysis | Customer count and revenue by acquisition source | Compares channel volume with channel value |
    | Lifecycle Segment Analysis | Revenue and count by lifecycle group | Separates broad customer volume from high-value behavior |

    !!! success "So what?"

        Lifecycle and membership views help stakeholders distinguish customer volume from customer value. A smaller high-value group can drive more revenue than a much larger low-activity group.

=== "Method"

    This page is dbt-only. It does not use predictive modeling or notebooks.

    ## dbt Model Flow

    | Layer | Models | Purpose |
    | --- | --- | --- |
    | Staging | `stg_users`, `stg_interactions` | Standardize corrected user and transaction data |
    | Mart | `mart_customer_overview` | Produces one row per customer with profile fields and transaction metrics |

    ## Customer Mart Fields

    `mart_customer_overview` combines:

    | Field group | Examples |
    | --- | --- |
    | Profile | membership tier, primary device, market, acquisition source, user segment, lifecycle segment, join date |
    | Activity | transaction count, completed transaction count, first order date, last order date |
    | Value | total revenue, average order value |
    | Recency | customer age and days since last order |

    !!! tip "Why this matters"

        The Tableau page is built from customer-level records, so membership, acquisition, lifecycle, and revenue can be compared without re-aggregating raw transactions in the dashboard.
