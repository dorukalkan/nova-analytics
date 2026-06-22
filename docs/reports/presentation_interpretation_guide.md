---
icon: lucide/presentation
title: Presentation Interpretation Guide
description: Business-facing interpretation guide for the geography analysis findings
---

# Presentation Interpretation Guide

This page summarizes how to explain the geography analysis findings to a non-technical audience. The goal is to keep the story business-led: which markets look attractive, what explains local demand, and how markets group into strategic archetypes.

## Feature Importance

Feature importance answers:

```text
Which inputs helped the demand model explain daily transaction volume?
```

For this analysis, feature importance was calculated with **permutation importance**. In plain language, this means:

1. First, the model predicts demand on the validation period.
2. Then one input is shuffled, so the model can no longer use that input correctly.
3. If prediction error gets much worse, that input is important.

!!! note "Business interpretation"

    Feature importance shows predictive association, not causation. A feature can be important because it directly helps explain demand, or because it represents broader market maturity.

### Feature Families

| Feature family | What it contains | Business meaning |
| --- | --- | --- |
| Service supply | Active services, average rating, popularity, head/mid/long-tail service counts and shares | Marketplace depth and service quality |
| Category | Food Delivery, Ride Hailing, E-Commerce, Grocery, Digital Wallet | Different service verticals have different demand patterns |
| Market context | Market weight, growth multiplier, iOS share, population, GDP per capita, urbanization, internet and mobile indicators | Market potential and operating environment |
| Market identity | Market, region, country, latitude, longitude | Location-specific differences not fully captured by other fields |
| Weather | Rain, precipitation, temperature, wind, weather and precipitation bands | Local daily operating conditions |
| Calendar | Month, quarter, day of week, weekend flag | Seasonality and timing effects |

### Speaker Notes

Use this wording for a short presentation:

> After building the demand model, I wanted to understand which inputs helped the model explain daily transaction volume. To do that, I used a feature importance method called permutation importance. In simple terms, I tested each input by shuffling it in the validation data and checking how much worse the model became. If the prediction error increased a lot, that input was important because the model relied on it.
>
> The strongest family was service supply. This includes how many services are available in each market and category, average service rating, service popularity, and the mix of head, mid-tier, and long-tail services. From a business perspective, this means demand is closely tied to marketplace depth. Markets with more available and higher-quality services tend to have more predictable demand.
>
> Category came next, which tells us that demand behaves differently across Food Delivery, Ride Hailing, E-Commerce, Grocery, and Digital Wallet. Market context captures things like market size, growth multiplier, GDP per capita, internet usage, and mobile adoption. Weather and calendar features still matter, but in this model they were secondary.
>
> The key takeaway is not that service supply directly causes demand by itself. This is an association, not a causal experiment. But it gives a clear business signal: if Nova wants to understand or grow market demand, supply health should be analyzed alongside external factors like weather and macro context.

### Main Takeaway

The model suggests that daily demand is not explained only by external conditions such as weather or calendar timing. The strongest signal was **service supply**, meaning the depth and quality of the marketplace are closely associated with demand.

## Market Clustering

Clustering answers a different question from opportunity scoring:

```text
Which markets behave similarly?
```

Opportunity scoring ranks markets. Clustering groups markets into strategic archetypes based on similar profiles across demand scale, GMV, growth, service supply, reliability, macro context, category mix, and weather sensitivity.

### Cluster Interpretation

| Cluster label | Markets | Business meaning | How it differs |
| --- | --- | --- | --- |
| Broad monitor markets | Bangkok, Dubai, Ho Chi Minh City, Istanbul, Mexico City, Riyadh, Sao Paulo, Sydney | Meaningful presence, but less mature or less clearly prioritized | Lowest demand scale, service supply, and opportunity score |
| High-demand supply-led markets | Bangalore, Jakarta, Manila, Mumbai | Scaled operating markets where service depth supports demand | Highest daily transactions and strongest supply |
| Singapore: high-opportunity outlier | Singapore | Premium strategic market with strong macro and opportunity profile | Highest opportunity score; distinct enough to stand alone |
| Developed high-value growth markets | London, New York, Tokyo | Mature, high-value markets with strong growth and reliability | Higher GMV and growth; less weather-driven |

!!! warning "Modeling caveat"

    These clusters are exploratory. There are only 16 markets, so the labels are best used for storytelling and strategy discussion, not as final operating rules.

### Speaker Notes

Use this wording for a short presentation:

> After ranking markets by opportunity, I used clustering to group markets with similar business profiles. Unlike the demand model, clustering does not predict a target. It looks across market scale, GMV, growth, service supply, reliability, macro context, category mix, and weather sensitivity, then groups markets that behave similarly.
>
> The first group is Broad Monitor Markets: Bangkok, Dubai, Ho Chi Minh City, Istanbul, Mexico City, Riyadh, Sao Paulo, and Sydney. This is the largest group, but it has the lowest average daily demand, lowest service depth, and lowest opportunity score. I would treat these as markets to monitor and diagnose before making aggressive growth bets.
>
> The second group is High-Demand Supply-Led Markets: Bangalore, Jakarta, Manila, and Mumbai. These markets have the strongest transaction volume and deepest service supply. The business story is that demand is already scaled, and service availability appears central to sustaining it.
>
> Singapore is its own cluster because it behaves differently. It has the strongest opportunity score and macro potential, with solid reliability and demand, but it is not simply another supply-heavy market. I would position Singapore as a strategic high-opportunity outlier.
>
> The final group is Developed High-Value Growth Markets: London, New York, and Tokyo. These markets are not the highest in transaction volume, but they show strong GMV, strong completion rates, and the highest growth profile. The story here is value and quality, not just scale.
>
> The key takeaway is that Nova should not use one market strategy everywhere. Some markets need supply protection, some need monitoring, Singapore deserves separate strategic attention, and developed markets should be managed around high-value growth.

### Main Takeaway

The clustering analysis turns the market list into different growth playbooks:

- **Protect and deepen supply** in high-demand supply-led markets.
- **Diagnose before scaling** broad monitor markets.
- **Treat Singapore separately** as a high-opportunity outlier.
- **Manage developed markets around value and growth**, not only transaction count.
