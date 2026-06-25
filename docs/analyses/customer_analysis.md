---
icon: lucide/user-round-check
title: Customer Analysis
description: Customer segmentation and lifecycle behavior dashboard
author: Merve Kaymaz
---

# Customer Analysis

![Tableau Customer Analysis Dashboard](../assets/6_customer_analysis.jpeg)

=== "Insights"

    Customer Analysis shows that Nova's customer value is highly concentrated. Premium members are a minority of the user base, but they contribute most completed revenue. High Value lifecycle customers show the same pattern: smaller in count, much larger in economic impact.

    !!! abstract "Key takeaway"

        Nova should manage customer growth around value concentration, not user count alone. Premium conversion, high-value retention, and channel quality matter more than broad acquisition volume.

    ## Key Findings

    | Finding | Metric | Interpretation |
    | --- | --- | --- |
    | Premium members are a minority | **25.28% of customers** are Gold or Platinum | The premium base is still small enough to grow |
    | Premium members carry most completed revenue | About **$1.56B of $2.36B** completed revenue | Membership tier is strongly tied to customer value |
    | Platinum customers are the highest-value tier | **$5,397** average completed revenue per customer | Platinum behavior is the clearest high-value benchmark |
    | Gold customers also outperform Standard | **$2,374 vs $534** average completed revenue per customer | Upgrading Standard customers could materially improve customer economics |
    | Organic Search is the largest acquisition channel | **32.14%** of customers and **$756.64M** completed revenue | Organic discovery is both the biggest user source and the largest revenue channel |
    | High Value customers dominate lifecycle revenue | **199K** customers generate **$1.44B** completed revenue | The most valuable lifecycle group is much smaller than the largest customer group |

    ## Business Insights

    Membership tier is the clearest value signal on this page. Standard customers make up most of the base, but Platinum and Gold customers generate far more value per customer. That suggests the main customer opportunity is not only acquiring more users, but moving the right users into higher-value behavior.

    Acquisition quality also matters. Organic Search brings both the largest customer count and the largest completed revenue, while Push Notification is smaller by volume but has the highest average completed revenue per customer among acquisition sources. Channel strategy should separate scale from efficiency.

    Lifecycle segmentation makes the retention priority clear. Retained customers are the largest group at about **1.09M** users and **$821.71M** completed revenue, but High Value customers generate more revenue from a much smaller base. Inactive customers are large in count, at about **300K**, but contribute almost no current value.

    !!! success "Recommendation"

        Prioritize premium conversion and High Value retention first, keep Organic Search strong as the main acquisition engine, and use lower-volume channels like Push Notification for targeted high-value engagement rather than broad reach.

=== "Method"

    This page includes the dbt models used for the analysis.

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
