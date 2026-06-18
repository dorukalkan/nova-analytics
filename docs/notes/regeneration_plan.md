---
icon: lucide/target
title: Dataset Regeneration Plan
---

# Data Regeneration, QA, and Modeling Context

This document summarizes the current state of the Nova analytics dataset and the recommended plan for regenerating/correcting the synthetic data before downstream modeling and dashboard work.

It is intended as context for Codex / VS Code development.

---

## 1. Project Context

Nova is a synthetic super-app analytics project with 50M transaction-level records across 16 city markets and 5 major service categories.

The current stack/workflow:

- Kaggle / local notebooks for exploration and modeling
- Google Cloud Storage for raw file staging
- BigQuery as the warehouse
- dbt for staging/intermediate/mart transformations
- Power BI or Streamlit for dashboard/reporting
- Python / scikit-learn for modeling

The current geography analysis track is:

**Geo Market Opportunity & Local Demand Drivers**

Main business question:

> Which Nova markets have the strongest expansion opportunity, and what local conditions help explain market-level demand?

The analysis should stay market-led. Weather is not the whole story; it is one external feature family inside a broader demand and market opportunity model.

---

## 2. Current Market Scope

There are 16 markets:

```text
Singapore
Jakarta
Manila
Bangkok
Ho Chi Minh City
Istanbul
Dubai
Riyadh
London
New York
Mexico City
Sao Paulo
Mumbai
Bangalore
Tokyo
Sydney
```

There are 5 categories:

```text
Digital Wallet
E-Commerce
Food Delivery
Grocery
Ride Hailing
```

The core modeling grain for geography should be:

```text
one row = market_id + category + order_date
```

Expected size for full-year 2024:

```text
16 markets × 5 categories × 366 days = 29,280 rows
```

This is the correct grain for market/category/day demand modeling.

---

## 3. Current dbt Model Structure

The current dbt geography track is structurally sound.

### Seeds

External seed context includes:

- `market_country_lookup`
- `ext_weather_daily`
- `ext_world_bank_indicators`
- `ext_country_metadata`

### Staging

Staging models should remain thin and analysis-safe:

- `stg_geo_market_country_lookup`
- `stg_geo_weather_daily`
- `stg_geo_world_bank_indicators`
- `stg_geo_country_metadata`

Staging responsibilities:

- Standardize column names
- Preserve source grain
- Avoid business scoring logic
- Add safe casts / renames only

### Intermediate

Intermediate geography models include:

- `int_geo_country_macro_pivot`
- `int_geo_market_context`
- `int_geo_date_spine`
- `int_geo_market_category_spine`
- `int_geo_market_day_metrics`
- `int_geo_market_category_day_metrics`
- `int_geo_service_supply_by_market_category`

This layer is responsible for:

- Spines
- Joins
- Base aggregates
- Reusable building blocks

### Marts

Important geography marts:

- `mart_geo_market_opportunity`
- `mart_geo_market_category_day_features`
- `mart_geo_weather_category_sensitivity`

The main modeling mart should be:

```text
mart_geo_market_category_day_features
```

with expected grain:

```text
market_id + category + order_date
```

---

## 4. Important Correction: Export Issue vs Table Issue

A previous BigQuery export only contained around 10k rows because BigQuery UI query result export could not save all 29k rows.

This was an export limitation, not necessarily a dbt table problem.

Still, every regeneration/build should verify the mart itself has full coverage.

Expected:

```text
rows: 29,280
markets: 16
categories: 5
dates: 366
min_date: 2024-01-01
max_date: 2024-12-31
```

---

## 5. Main Data Realism Issues Identified

The team identified the following issues/risks:

1. Repeat user behavior is flat.
2. Category/service ratings seem synthetic.
3. Transaction amount distribution across markets and dimensions is too uniform.
4. Monthly growth pattern is the same while only levels differ.
5. Customer/user dimension has not yet been deeply inspected and likely has issues.
6. Fraud analytics may not be possible unless transaction-level fraud/suspicious behavior is added.
7. Market-based category and transaction distributions need review.
8. Transaction status distribution needs realism across market/category/weather/service/user dimensions.
9. Weather effects must be realistic by market/category/service and include extreme weather, not just rain.
10. Downstream models should not break.
11. Existing table names, column names, grains, and category/status labels should be preserved as much as possible.
12. Internal consistency and reconciliation must be maintained after regeneration.

---

## 6. Preserve Downstream Contracts

Avoid breaking downstream dbt models.

### Preserve

Do not rename or change without a strong reason:

```text
table names
column names
primary keys
foreign keys
category labels
market IDs
status labels
date range
transaction grain
```

### Safe Changes

These are generally safe if done behind the existing column contracts:

```text
Regenerate transaction amounts.
Regenerate status probabilities.
Regenerate timestamps / demand distribution.
Regenerate service ratings and popularity.
Regenerate user repeat behavior.
Regenerate weather-sensitive demand.
Regenerate promo flags/shares if already present.
Regenerate fraud/suspicious patterns if needed.
```

### Higher-Risk Changes

Avoid unless necessary:

```text
Renaming columns.
Dropping fields.
Changing category labels.
Changing status names.
Changing market IDs.
Changing date parsing conventions.
Changing transaction grain.
Changing raw/staging contracts silently.
```

If adding new fields, propagate them intentionally through staging, intermediate, and mart layers.

---

## 7. QA Checks Required After Every Regeneration

Before modeling or dashboard work, run these checks.

### 7.1 Mart grain coverage

```sql
select
  count(*) as rows,
  count(distinct market_id) as markets,
  count(distinct category) as categories,
  count(distinct order_date) as dates,
  min(order_date) as min_date,
  max(order_date) as max_date
from {{ ref('mart_geo_market_category_day_features') }};
```

Expected:

```text
rows = 29280
markets = 16
categories = 5
dates = 366
min_date = 2024-01-01
max_date = 2024-12-31
```

### 7.2 Missing market-category-date combinations

```sql
select
  market_id,
  market_name,
  category,
  count(*) as observed_days
from {{ ref('mart_geo_market_category_day_features') }}
group by 1, 2, 3
having count(*) != 366
order by observed_days;
```

Expected:

```text
0 rows
```

### 7.3 Duplicate grain rows

```sql
select
  market_id,
  category,
  order_date,
  count(*) as row_count
from {{ ref('mart_geo_market_category_day_features') }}
group by 1, 2, 3
having count(*) > 1;
```

Expected:

```text
0 rows
```

### 7.4 Status reconciliation

```sql
select
  sum(transactions) as transactions,
  sum(completed_transactions + failed_transactions + refunded_transactions) as status_total
from {{ ref('mart_geo_market_category_day_features') }};
```

Expected:

```text
transactions = status_total
```

If statuses are not mutually exhaustive, document why and adjust the check.

### 7.5 Category totals reconcile to market totals

```sql
with category_day as (
  select
    market_id,
    order_date,
    sum(transactions) as category_transactions,
    sum(gmv_usd) as category_gmv_usd
  from {{ ref('mart_geo_market_category_day_features') }}
  group by 1, 2
),

market_day as (
  select
    market_id,
    order_date,
    transactions as market_transactions,
    gmv_usd as market_gmv_usd
  from {{ ref('int_geo_market_day_metrics') }}
)

select
  c.market_id,
  c.order_date,
  c.category_transactions,
  m.market_transactions,
  c.category_transactions - m.market_transactions as transaction_diff,
  c.category_gmv_usd,
  m.market_gmv_usd,
  c.category_gmv_usd - m.market_gmv_usd as gmv_diff
from category_day c
join market_day m
  on c.market_id = m.market_id
 and c.order_date = m.order_date
where
  abs(c.category_transactions - m.market_transactions) > 0
  or abs(c.category_gmv_usd - m.market_gmv_usd) > 0.01;
```

Expected:

```text
0 rows
```

### 7.6 Category mix sanity

```sql
select
  market_name,
  category,
  safe_divide(
    sum(transactions),
    sum(sum(transactions)) over(partition by market_name)
  ) as category_share
from {{ ref('mart_geo_market_category_day_features') }}
group by 1, 2
order by market_name, category_share desc;
```

Inspect manually.

Problem signs:

```text
Every market has almost identical category shares.
Digital Wallet is weather-sensitive in the same way as Ride Hailing/Food Delivery.
Category shares are too uniform across markets.
```

### 7.7 Monthly growth pattern sanity

```sql
with monthly as (
  select
    market_name,
    date_trunc(order_date, month) as order_month,
    sum(transactions) as monthly_transactions
  from {{ ref('mart_geo_market_category_day_features') }}
  group by 1, 2
),

growth as (
  select
    market_name,
    order_month,
    monthly_transactions,
    safe_divide(
      monthly_transactions - lag(monthly_transactions) over (
        partition by market_name order by order_month
      ),
      lag(monthly_transactions) over (
        partition by market_name order by order_month
      )
    ) as mom_growth
  from monthly
)

select *
from growth
order by market_name, order_month;
```

Inspect manually.

Problem sign:

```text
All markets have nearly identical month-over-month growth curves.
```

### 7.8 Service rating spread

```sql
select
  category,
  count(*) as services,
  avg(rating) as avg_rating,
  stddev(rating) as std_rating,
  min(rating) as min_rating,
  approx_quantiles(rating, 10) as rating_deciles,
  max(rating) as max_rating
from {{ ref('stg_services') }}
group by 1
order by category;
```

Problem sign:

```text
Ratings are compressed around ~4.39 with tiny standard deviation.
```

### 7.9 User repeat behavior

Exact table/model names may differ. The goal is to inspect skew and repeat behavior.

```sql
select
  count(*) as users,
  avg(user_transactions) as avg_user_transactions,
  approx_quantiles(user_transactions, 20) as transaction_quantiles,
  max(user_transactions) as max_user_transactions
from (
  select
    user_id,
    count(*) as user_transactions
  from {{ ref('stg_nova_interactions') }}
  group by 1
);
```

Problem signs:

```text
Most users have almost the same number of transactions.
No long tail of power users.
No meaningful one-time/casual/regular/power-user segmentation.
```

---

## 8. Data Regeneration Priorities

Recommended correction order:

```text
1. Full date coverage / feature mart completeness
2. Monthly growth pattern by market/category
3. Repeat user heterogeneity
4. Transaction amount distribution
5. Category mix by market
6. Service ratings/popularity
7. Status/failure/refund variation
8. Promo behavior
9. Weather sensitivity
10. Optional fraud/suspicious behavior
```

Weather is important, but if monthly growth and repeat users are flat, modeling will still feel artificial.

---

## 9. Monthly Growth Correction

Current issue:

```text
Markets have different transaction levels, but nearly identical monthly change patterns.
```

This is too synthetic.

Better generation formula:

```text
demand =
  base_demand
  × global_month_factor
  × region_month_factor
  × market_month_factor
  × category_month_factor
  × market_category_affinity
  × day_of_week_factor
  × promo_factor
  × weather_factor
  × random_noise
```

Key idea:

```text
Keep a global seasonal trend, but add market/category-specific deviations.
```

Example behavior:

```text
New York and London can share some winter/holiday patterns.
Mumbai and Jakarta can share some monsoon sensitivity.
Dubai and Riyadh can share heat-season behavior.
But no two markets should have identical monthly growth curves.
```

---

## 10. Repeat User Behavior Correction

Repeat behavior should be heterogeneous.

Create user segments such as:

```text
one_time_users
casual_users
regular_users
power_users
multi_service_loyalists
promo_driven_users
high_value_users
dormant_or_churn_risk_users
```

Repeat behavior should vary by:

```text
membership tier
primary device
market
category
first service used
join cohort
promo exposure
service experience
failed/refunded transaction history
```

Useful downstream metrics:

```text
repeat_rate
days_between_transactions
active_days_per_user
transactions_per_active_user
multi_service_user_share
first_30d_retention
cohort retention by join month
```

Distribution target:

```text
Many low-frequency users.
Moderate number of regular users.
Small number of high-frequency/power users.
```

Avoid:

```text
Every user transacts at similar frequency.
Repeat rate is identical across markets/categories.
Membership tier has no behavioral effect.
```

---

## 11. Transaction Amount Distribution Correction

Current issue:

```text
Average transaction amount is too uniform across markets.
```

Category-level amount pattern is useful:

```text
E-Commerce: higher
Grocery: high
Digital Wallet: medium
Food Delivery: lower
Ride Hailing: lower/medium
```

But market-level and market-category-level amounts should vary more.

Recommended generation structure:

```text
amount_usd =
  category_base_amount
  × market_price_index
  × market_category_amount_multiplier
  × service_tier_multiplier
  × promo_or_discount_effect
  × lognormal_noise
```

Potential market logic:

```text
Dubai, New York, London, Singapore: higher price levels
Mumbai, Jakarta, Manila, Ho Chi Minh City: lower average amount, but high volume
Riyadh/Dubai: stronger premium ride/e-commerce effect
Tokyo/Sydney: higher price levels
```

Use lognormal noise rather than normal noise for transaction amounts.

---

## 12. Category Mix by Market

Current issue:

```text
Category shares are too uniform across markets.
```

Add market-category affinity.

Example qualitative direction:

```text
Singapore:
  strong Digital Wallet, Food Delivery, E-Commerce

Jakarta / Manila / Ho Chi Minh City:
  strong Ride Hailing, Food Delivery, Digital Wallet

Mumbai / Bangalore:
  strong Ride Hailing, Digital Wallet, Food Delivery

Dubai / Riyadh:
  strong Ride Hailing, E-Commerce, Digital Wallet
  heat-sensitive Food Delivery/Grocery

London / New York:
  strong Ride Hailing, Food Delivery, E-Commerce
  weather/commute sensitivity

Istanbul:
  balanced but strong Food Delivery / Ride Hailing potential

Tokyo:
  strong E-Commerce / Food Delivery / Digital Wallet

Sydney:
  balanced, slightly higher E-Commerce/Ride Hailing
```

Do not force exact real-world truth. Just avoid identical synthetic shares.

---

## 13. Service Ratings and Popularity Correction

Current issue:

```text
Ratings are compressed and synthetic.
```

Better behavior:

```text
head-tier services:
  higher average rating
  lower variance
  higher popularity
  higher transaction share

mid-tier services:
  medium rating
  medium variance
  medium popularity

long-tail services:
  wider rating range
  lower popularity
  more noisy performance
```

Ratings should vary by:

```text
service tier
category
market maturity
transaction volume
operational reliability
```

Avoid making every market/category average rating close to the same value.

---

## 14. Status Distribution Correction

Current useful behavior:

```text
Digital Wallet has higher completion.
Food Delivery is relatively reliable.
Ride Hailing and E-Commerce can have lower completion.
```

Keep category-level status differences.

But add more variation by:

```text
market operational quality
weather severity
service tier
category difficulty
promo pressure
transaction amount anomaly
user risk
```

Suggested direction:

```text
Digital Wallet:
  highest completion
  low refund/failure
  suspicious/fraud cases may increase failure/refund if fraud is added

Food Delivery:
  good completion normally
  lower completion in heavy rain/storm/extreme heat

Grocery:
  moderate completion
  weather can affect fulfillment

Ride Hailing:
  lower completion in heavy rain/high wind
  cancellation/failure sensitive to weather

E-Commerce:
  refund/failure can be higher than wallet/food
  amount and service tier can affect risk
```

---

## 15. Promo Behavior

Current issue in the inspected export:

```text
promo_share appeared to be zero.
```

If promo fields already exist downstream, regenerate non-zero promo behavior.

Promo should vary by:

```text
market
category
date/month
growth strategy
membership tier
user lifecycle
```

Possible behavior:

```text
Growth markets: higher promo intensity.
Food Delivery/Grocery/E-Commerce: more promo-sensitive.
Digital Wallet: acquisition campaigns, not daily weather-sensitive promos.
Ride Hailing: commute/event/weather promos possible.
```

Promo should affect:

```text
transactions ↑
average amount may decrease if discounts are represented
repeat behavior may increase temporarily
margin/profitability if modeled
```

---

## 16. Weather Effects: General Principles

Weather can be a meaningful demand driver, but effects must be:

```text
market-specific
category-specific
severity-specific
anomaly-based
operationally consistent
```

Do not use only:

```text
is_rain_day
```

Rain means different things in Singapore, Dubai, Mumbai, London, and Istanbul.

Use market-relative weather features.

### Recommended weather anomaly features

Add or compute:

```text
temp_mean_vs_market_month_avg
temp_mean_market_month_zscore
precip_vs_market_month_avg
precip_market_month_zscore
wind_vs_market_month_avg
wind_market_month_zscore
is_heavy_rain_market_p90
is_extreme_heat_market_month_p90
is_extreme_cold_market_month_p10
is_high_wind_market_p90
```

### Weather severity concepts

Recommended flags:

```text
is_light_rain
is_moderate_rain
is_heavy_rain
is_extreme_heat
is_extreme_cold
is_high_wind
is_storm_like_day
is_bad_weather_day
```

These can be generated in dbt from `ext_weather_daily`.

---

## 17. Weather Effects by Category

### Ride Hailing

Expected:

```text
Rain/bad weather increases latent demand.
Heavy rain/high wind can reduce completion.
Extreme heat can increase ride demand in hot markets.
Cold/rain can increase ride demand in temperate markets.
```

Suggested demand effects:

```text
light rain: +3% to +8%
moderate rain: +8% to +18%
heavy rain: +15% to +30%
extreme heat: +3% to +12%
extreme cold: +3% to +10%
high wind: mixed demand, worse reliability
```

Operational effect:

```text
heavy rain/high wind:
  completion_rate down
  failed/cancelled/refunded up
```

### Food Delivery

Expected:

```text
Rain/heat/cold increases stay-home behavior and delivery demand.
Heavy weather worsens delivery reliability.
```

Suggested demand effects:

```text
light rain: +2% to +6%
moderate rain: +5% to +12%
heavy rain: +10% to +22%
extreme heat: +5% to +15%
extreme cold: +3% to +10%
```

Operational effect:

```text
heavy rain/storm/extreme heat:
  completion_rate down
  failed/refunded up
```

### Grocery

Expected:

```text
Bad weather mildly increases online grocery.
Basket size may increase more than transaction count.
Extreme weather can constrain fulfillment.
```

Suggested effects:

```text
light/moderate rain: +1% to +6%
heavy rain: +4% to +12%
extreme heat: +2% to +8%
```

Amount effect:

```text
bad weather → avg basket/amount slightly up
```

### E-Commerce

Expected:

```text
Weak/mixed weather effect.
Weather may shift browsing/purchasing online.
Effect depends strongly on product category, which may not exist in the dataset.
```

Suggested effects:

```text
rain/cold/bad weather: +0% to +5%
pleasant weather: -1% to -4%
extreme heat: +1% to +6%
```

Keep small unless product category detail is modeled.

### Digital Wallet

Expected:

```text
Weak direct weather effect.
Mostly indirect through other weather-sensitive categories.
```

Suggested effects:

```text
direct weather effect: 0% to +2%
```

Digital Wallet should not be more rain-sensitive than Ride Hailing or Food Delivery.

---

## 18. Weather Effects by Market Type

### Rain-sensitive / tropical / monsoon markets

```text
Mumbai
Jakarta
Manila
Bangkok
Ho Chi Minh City
Singapore
```

Important:

```text
Normal rain is less shocking in these markets.
Heavy/anomalous rain matters more.
Use rain anomaly or percentile thresholds.
```

### Heat-sensitive arid markets

```text
Dubai
Riyadh
```

Important:

```text
Extreme heat matters more than rain.
Rain is rare and may behave as an anomaly.
```

### Temperate / seasonal markets

```text
London
New York
Istanbul
Tokyo
Sydney
Sao Paulo
Mexico City
Bangalore
```

Important:

```text
Rain, wind, heat/cold anomalies, and seasonality can all matter.
```

---

## 19. Weather Sensitivity Mart Improvements

Current sensitivity mart is useful but should be expanded beyond rain/non-rain.

Add fields such as:

```text
heavy_rain_days
non_heavy_rain_days
avg_heavy_rain_day_transactions
heavy_rain_transaction_lift_pct

moderate_or_heavy_rain_days
moderate_or_heavy_rain_lift_pct

extreme_heat_days
extreme_heat_transaction_lift_pct

extreme_cold_days
extreme_cold_transaction_lift_pct

high_wind_days
high_wind_completion_rate_delta

storm_like_days
storm_like_transaction_lift_pct
storm_like_completion_rate_delta

weather_sensitive_category_expected_direction
observed_vs_expected_flag
```

Use this mart as a diagnostic after regeneration.

Expected pattern:

```text
Ride Hailing: strongest weather sensitivity
Food Delivery: strong weather sensitivity
Grocery: mild/moderate
E-Commerce: weak/mixed
Digital Wallet: near-zero direct
```

---

## 20. Fraud Analytics Feasibility

Fraud analytics is possible only if there is meaningful transaction-level suspicious behavior.

Fraud should not be invented only at aggregate mart level.

Useful fraud/suspicious behavior signals:

```text
many transactions in short time
failed transaction bursts
refund/chargeback-like outcomes
large amount anomalies
same user across many services/markets
same device/payment method across many users
new user + high amount + high failure/refund pattern
Digital Wallet cash-in/cash-out-like behavior
GPS anomaly / impossible travel
```

If the raw dataset lacks fields like device ID, payment method, merchant/service ID, user join date, user market, timestamps, and status, fraud will be shallow.

### Recommended fraud design if added

Add transaction-level fields only if the team agrees downstream changes are worth it:

```text
is_suspicious_transaction
fraud_risk_score
```

Possible rate:

```text
0.5% to 2.0% suspicious transactions overall
higher in Digital Wallet
medium in E-Commerce
low in Food Delivery/Grocery/Ride Hailing
```

Suspicious probability should correlate with:

```text
new users
high transaction velocity
failed/refunded status
amount anomalies
repeated service/device/payment patterns
unusual market/category behavior
```

If avoiding new columns, create derived fraud-risk marts using existing fields, but acknowledge the limitations.

---

## 21. Customer/User Dimension Review

The user/customer dimension needs explicit inspection.

Recommended checks:

```sql
select
  membership_tier,
  primary_device,
  count(*) as users
from {{ ref('stg_nova_users') }}
group by 1, 2
order by users desc;
```

```sql
select
  date_trunc(join_date, month) as join_month,
  membership_tier,
  count(*) as users
from {{ ref('stg_nova_users') }}
group by 1, 2
order by join_month, membership_tier;
```

Transaction behavior by user:

```sql
with user_tx as (
  select
    user_id,
    count(*) as transactions,
    count(distinct category) as categories_used,
    count(distinct order_date) as active_days,
    min(order_date) as first_order_date,
    max(order_date) as last_order_date,
    sum(amount_usd) as total_gmv_usd
  from {{ ref('stg_nova_interactions') }}
  group by 1
)

select
  count(*) as users,
  avg(transactions) as avg_transactions,
  approx_quantiles(transactions, 20) as transaction_quantiles,
  approx_quantiles(categories_used, 5) as categories_used_quantiles,
  approx_quantiles(active_days, 20) as active_days_quantiles,
  max(transactions) as max_transactions
from user_tx;
```

Desired behavior:

```text
Some one-time users.
Some casual users.
Some regular users.
Small group of power users.
Multi-service users should retain/transact more.
Membership tier should matter.
Device and market should have plausible differences.
```

---

## 22. Modeling Plan

Do not start with complex ML immediately.

Use the following sequence.

### Step 1 — Baseline model

Target:

```text
transactions
```

or:

```text
log1p(transactions)
```

Baseline features:

```text
market
category
day_of_week
is_weekend
month
market_weight
growth_multiplier
active_services
avg_service_rating
```

Benchmark options:

```text
market-category historical average
market-category day-of-week average
seasonal/monthly average
```

### Step 2 — Weather-enriched model

Add:

```text
precipitation_sum_mm
temperature_2m_mean_c
wind_speed_10m_max_kmh
precip_market_month_zscore
temp_market_month_zscore
is_heavy_rain_market_p90
is_extreme_heat_market_month_p90
is_extreme_cold_market_month_p10
category × weather interactions
market climate segment × weather interactions
```

Compare:

```text
baseline model vs weather-enriched model
```

Metrics:

```text
MAE
RMSE
MAPE
WMAPE
R²
```

Preferred evaluation split:

```text
train: Jan–Oct 2024
validation: Nov–Dec 2024
```

### Step 3 — Interpretable model first

Start with:

```text
Ridge regression / ElasticNet
```

Then optionally:

```text
Random Forest
HistGradientBoostingRegressor
XGBoost / LightGBM only if needed
```

### Step 4 — Optional classification target

Use:

```text
is_high_demand_day
```

But define it correctly:

```text
transactions >= p75 within same market/category
```

Avoid a global threshold that makes high-demand days rare or category-skewed.

---

## 23. Avoid ML Leakage

Do not use target-derived fields as predictors when predicting transactions.

Potential leakage fields:

```text
avg_market_category_daily_transactions
p75_market_category_daily_transactions
is_high_demand_day
demand_index_vs_market_category_avg
```

Use them as:

```text
diagnostics
labels
BI metrics
target helpers
```

not as independent features.

If predicting `is_high_demand_day`, then `is_high_demand_day` is the target and must not appear in `X`.

---

## 24. Dashboard Story Requirements

Every chart should support a coherent business story.

The geography dashboard can be two pages.

### Page 1: Market Opportunity Atlas

Question:

```text
Which markets should Nova scale, fix, maintain, or monitor?
```

Possible visuals:

```text
Bubble map by market
Market leaderboard
Macro opportunity vs Nova performance scatter
Region/category slicers
Service supply and reliability comparison
```

### Page 2: Local Demand Drivers

Question:

```text
Which local conditions and internal signals explain demand variation?
```

Possible visuals:

```text
Actual vs predicted demand
Feature importance
Weather sensitivity by market/category
Heavy rain / extreme heat demand lift
Completion-rate impact under severe weather
Market-category demand matrix
```

---

## 25. Recommended Implementation Phases

### Phase 1 — QA and diagnostics

Create reusable SQL/dbt tests or analysis queries for:

```text
row counts
grain uniqueness
foreign key coverage
status reconciliation
GMV reconciliation
full date coverage
market/category completeness
monthly growth curves
category shares
amount distributions
ratings spread
user repeat behavior
weather sensitivity
```

### Phase 2 — Regenerate corrected data

Fix:

```text
monthly growth variation
repeat user heterogeneity
transaction amount distributions
category mix by market
service rating/popularity spread
status/reliability variation
promo behavior
weather effects
optional fraud signal
```

### Phase 3 — Rebuild dbt

Run:

```bash
uv run dbt build
```

Then inspect:

```text
mart_geo_market_opportunity
mart_geo_market_category_day_features
mart_geo_weather_category_sensitivity
customer/user behavior marts
fraud/suspicion marts if added
```

### Phase 4 — Modeling prototype

Build notebook:

```text
baseline demand model
weather-enriched demand model
feature importance
prediction export
market/category diagnostics
```

### Phase 5 — Dashboard

Build Power BI/Streamlit pages only after the corrected marts are stable.

---

## 26. Recommended Codex Tasks

Use these as concrete implementation tasks.

### Task A — Add QA SQL analyses

Create `analyses/qa/` files:

```text
qa_mart_geo_market_category_day_coverage.sql
qa_status_reconciliation.sql
qa_market_category_mix.sql
qa_monthly_growth_patterns.sql
qa_user_repeat_behavior.sql
qa_weather_sensitivity_sanity.sql
```

### Task B — Add weather anomaly intermediate model

Create:

```text
models/intermediate/geography/int_geo_weather_anomaly_features.sql
```

Expected grain:

```text
market_id + weather_date
```

Add:

```text
market-month weather averages
temperature z-scores
precipitation z-scores
wind z-scores
heavy rain flags
extreme heat/cold flags
high wind flags
bad weather flags
```

### Task C — Extend market-category-day feature mart

Add weather anomaly fields to:

```text
mart_geo_market_category_day_features
```

without breaking existing columns.

### Task D — Improve weather sensitivity mart

Extend:

```text
mart_geo_weather_category_sensitivity
```

with heavy rain, extreme heat/cold, high wind, and storm-like comparisons.

### Task E — Build user behavior diagnostics

Create user-level intermediate/mart models:

```text
int_user_transaction_summary
mart_user_lifecycle_segments
```

Only if aligned with team scope.

### Task F — Fraud feasibility diagnostics

Create a diagnostic model first:

```text
mart_fraud_signal_feasibility
```

Do not add final fraud claims until the raw data supports them.

---

## 27. Final Recommendation

Do not start final modeling until the regenerated dataset passes QA and shows plausible variation.

The project direction is strong:

```text
Market Opportunity + Local Demand Drivers
```

But the dataset needs correction so the story is defensible.

Highest-priority corrections:

```text
1. Market/category-specific growth curves
2. Repeat user heterogeneity
3. Transaction amount variation
4. Category mix by market
5. Service rating/popularity spread
6. Status/reliability variation
7. Promo behavior
8. Weather anomaly effects
9. Optional fraud signal
```

The strongest modeling story will be:

> We tested whether local conditions, service supply, platform behavior, and weather anomalies explain daily market-category demand beyond baseline seasonality and market/category effects.

This is a credible analytics story and a good fit for dbt + BigQuery + Python + BI.
