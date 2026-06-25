---
icon: lucide/chart-bar
title: Category Performance
description: Category-level revenue, risk, quality, repeat behavior, and growth opportunity dashboard
author: Yasemen Nur Salım Dündar
---

# Category Performance Intelligence

=== "Insights"

    ![Tableau Category Performance Dashboard](../assets/4_category.png)

    Category Performance Intelligence compares Nova's service categories across revenue contribution, service quality, operational risk, repeat behavior, and growth potential.

    !!! abstract "What this page answers"

        - Which categories contribute the most revenue?
        - Which categories carry the highest operational risk?
        - Which services need intervention?
        - Where should growth investment be prioritized?

    ## KPI Cards

    | KPI | What it shows | Why it matters |
    | --- | --- | --- |
    | Critical Services | Number of services classified as operationally critical | Highlights where immediate service-level attention is needed |
    | Average Rating | Average customer rating across services | Tracks category-level service quality |
    | Repeat User Rate | Share of users who interact with the same service multiple times | Shows whether a category is building durable customer behavior |

    ## Dashboard Views

    | View | What it shows | Business use |
    | --- | --- | --- |
    | Revenue-Risk Matrix | Category revenue share, revenue loss rate, and total revenue | Finds large categories with meaningful risk exposure |
    | Service Performance Scorecard | Service-level revenue, success, refund, failure, and risk segment | Identifies services needing operational attention |
    | Service Risk Distribution | Risk segment counts by category | Distinguishes isolated service issues from broad category risk |
    | Growth Opportunity Ranking | Category scale and execution quality | Prioritizes categories for expansion or stabilization |

    !!! success "So what?"

        Categories with strong revenue and high success rates are better candidates for growth. Categories with high revenue but weaker reliability should be stabilized before additional investment.

=== "Method"

    This analysis is built with dbt service-health and category-health models. It does not use predictive modeling.

    ## dbt Model Flow

    | Layer | Models | Purpose |
    | --- | --- | --- |
    | Staging | `stg_interactions`, `stg_services`, `stg_markets` | Standardize corrected transaction, service, and market data |
    | Intermediate | `int_services_enriched`, `int_service_interactions`, `int_service_health`, `int_service_risk`, `int_category_health` | Join services to interactions, aggregate service performance, classify service risk, and roll up category health |
    | Mart | `mart_category_performance`, `mart_category_market_performance`, `mart_marketplace_service` | Provide Tableau-ready category, market-category, and service-level reporting tables |

    ## Risk Logic

    Service risk is assigned from operational signals:

    | Signal | Role |
    | --- | --- |
    | Success rate | Measures completed interaction reliability |
    | Failure rate | Flags services with elevated failure behavior |
    | Refund rate | Captures revenue and quality leakage |
    | Rating | Adds customer-facing service quality context |

    The category dashboard then rolls these service-level signals into category-level risk and growth views.

    !!! tip "Why this matters"

        The dashboard is not just visualizing raw category totals. It is built from a service-level health model, which lets category performance reflect both scale and operational quality.
