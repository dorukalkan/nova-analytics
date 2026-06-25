---
icon: lucide/repeat
title: RFM Analysis
description: Recency, frequency, and monetary customer segmentation dashboard
author: Merve Kaymaz
---

# RFM Analysis

=== "Insights"

    ![Tableau RFM Analysis Dashboard](../assets/7_rfm_analysis.jpeg)

    RFM Analysis segments customers using recency, frequency, and monetary value. It turns transaction history into business-friendly groups such as Champions, Loyal Customers, Potential Loyalists, At Risk, and Lost Customers.

    !!! abstract "What this page answers"

        - Which customer segment produces the most revenue?
        - Which segment contains the most customers?
        - Which segment has the highest average spend?
        - How do recency and frequency scores interact across the customer base?

    ## RFM Method

    | Signal | Meaning | Business interpretation |
    | --- | --- | --- |
    | Recency | How recently the customer ordered | Recent customers are easier to reactivate or retain |
    | Frequency | How often the customer ordered | Frequent customers show stronger engagement |
    | Monetary | How much the customer spent | High spenders carry more revenue value |

    ## Dashboard Signals

    | View | What it shows | Business use |
    | --- | --- | --- |
    | Customer Segment Distribution | Size of each RFM segment | Shows where the broadest customer base sits |
    | RFM Heatmap | Frequency and recency score concentration | Finds healthy and weak engagement patterns |
    | Revenue by Customer Segment | Total revenue by segment | Identifies the largest value pools |
    | Average Spend by Segment | Per-customer value by segment | Separates scale from individual value |

    !!! success "So what?"

        RFM gives Nova an action-oriented customer strategy: protect Champions, grow Potential Loyalists, reward Loyal Customers, and target At Risk or Lost Customers with reactivation campaigns.

=== "Method"

    This page is dbt-only. It uses rules-based segmentation, not predictive modeling or notebooks.

    ## dbt Model Flow

    | Model | Grain | Role |
    | --- | --- | --- |
    | `int_customer_metrics` | customer | Calculates transaction count, total spend, average order value, first and last order date, customer lifetime days, category count, and services used |
    | `int_rfm_features` | customer | Derives recency, frequency, and monetary fields |
    | `int_rfm_scores` | customer | Assigns 1-5 scores for recency, frequency, and monetary value |
    | `mart_customer_segments` | customer | Maps scores into business-friendly segment labels |

    ## Segment Logic

    | Segment | Rule interpretation |
    | --- | --- |
    | Champions | Recent, frequent, and high-value customers |
    | Loyal Customers | Strong frequency with acceptable recency |
    | New Customers | Recent customers with lower frequency |
    | Big Spenders | High monetary value with lower frequency |
    | At Risk | Previously active customers with weaker recency |
    | Lost Customers | Customers with the weakest recency |
    | Potential Loyalists | Customers who do not fall into the other explicit groups |

    !!! tip "Why this matters"

        RFM turns raw transaction history into a simple prioritization framework that can be used by marketing, retention, and customer strategy teams.
