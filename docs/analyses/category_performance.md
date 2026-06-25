---
icon: lucide/chart-bar
title: Category Performance
description: Category-level revenue, risk, quality, repeat behavior, and growth opportunity dashboard
author: Yasemen Nur Salım Dündar
---

# Category Performance Intelligence

![Tableau Category Performance Dashboard](../assets/4_category.png)

The Category Performance Intelligence dashboard compares Nova's service categories across revenue contribution, service quality, operational risk, repeat behavior, and growth potential.

!!! abstract "What this dashboard answers"

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

### Revenue-Risk Matrix

This bubble chart positions categories by revenue share and revenue loss rate, with bubble size representing total revenue.

!!! tip "How to read it"

    Categories in the high-revenue, high-risk area are the most important to monitor. They are large enough to affect overall performance and risky enough to create revenue leakage.

### Service Performance Scorecard

The scorecard lists service-level performance metrics such as risk segment, revenue, success rate, refund rate, and failure rate.

| Business question | Dashboard signal |
| --- | --- |
| Which services are underperforming? | Low success rate, high refund rate, or high failure rate |
| Which services need operational improvement? | Critical or high-risk service labels |
| Which categories have concentrated risk? | Multiple risky services in the same category |

### Service Risk Distribution

This view shows how services are distributed across risk levels within each category.

Use it to distinguish a category with a few isolated service issues from a category where risk is broad-based.

### Growth Opportunity Ranking

The ranking combines revenue volume and success rate to identify categories with both scale and execution quality.

!!! success "Business use"

    Categories with strong revenue and high success rates are better candidates for expansion. Categories with high revenue but weaker reliability should be stabilized before additional growth investment.

## Business Impact

This dashboard helps stakeholders monitor category health, reduce revenue concentration risk, prioritize service interventions, and identify scalable growth opportunities across the Nova marketplace.
