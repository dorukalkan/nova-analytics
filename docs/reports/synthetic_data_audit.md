# Nova Synthetic Data Audit

This report reviews `notebooks/nova_exploration.ipynb` and the raw parquet tables with a dashboard lens. The data is structurally clean, but several fields are synthetic enough that Power BI charts will look flat or misleading unless the project adds an analytics correction layer.

## Executive assessment

The dataset is usable for a final analytics project if we treat the raw tables as an immutable synthetic source and build curated marts that correct the unrealistic behavior. It is not safe to build final visuals directly from the notebook's current KPI parquet outputs.

Highest-risk issues:

- Interaction `Category` disagrees with `services.Category` for `40,018,166` of `50,000,000` rows, or `80.04%`.
- Monthly volume is almost entirely explained by the number of days in the month; `2024-12-31` is missing.
- Hourly transaction volume is nearly flat across all 24 hours.
- `Amount_USD` is uniform from `$5` to `$150` and has almost identical distributions across category, status, platform, and referral source.
- `Status` is fixed around `90% Completed`, `5% Failed`, `5% Refunded` across every dimension.
- Platform, referral source, category, amount, status, service, GPS, and user attributes behave mostly independently.
- All 2M users are active, repeat users; lifetime retention and cross-sell metrics are therefore not meaningful as currently defined.

## Notebook review by section

### Cells 2-9: loading and schema

These cells are technically sound. Polars lazy scanning is the right approach for the 2.6 GiB interaction table. The raw interaction table already includes `Timestamp_dt`, `Date`, `Month`, and `Hour`, even though the notebook describes them as derived fields.

Risk: `Timestamp` is a string in the raw schema while `Timestamp_dt` is typed. In BigQuery, ingest both but standardize downstream on a single typed timestamp.

### Cells 12-17: counts, keys, and nulls

The data passes basic quality checks perfectly:

- 50M interaction rows.
- 50M unique transaction UUIDs.
- 2M unique users.
- 50k unique services.
- Zero nulls in every table.

This is clean, but too perfect. Keep these as dbt tests, but add synthetic-behavior tests because null/uniqueness checks alone will make the dataset look healthier than it analytically is.

Suggested tests:

- `Transaction_UUID` unique and not null.
- `User_ID` and `Service_ID` relationship tests.
- Accepted values for `Status`, `Category`, `Membership_Tier`, `Primary_Device`.
- Custom warning tests for category mismatch rate, missing `2024-12-31`, flat hourly coefficient of variation, and GPS/global-uniform behavior.

### Cells 20-24: categorical profiling

The category and status shares are target-like:

- Category: Food Delivery `40.01%`, Ride Hailing `20.00%`, E-Commerce `20.00%`, Grocery `10.00%`, Digital Wallet `10.00%`.
- Status: Completed `90.00%`, Refunded `5.00%`, Failed `5.00%`.
- Platform: four user agents at almost exactly `25%` each.
- Referral source: five sources at almost exactly `20%` each.

These fields are too independent and too balanced for useful segmentation. They can still support broad dashboard slices, but differences between segments should not be interpreted as business findings unless adjusted.

### Cell 29: service/category consistency

This is the most important issue. The fact table category and service dimension category are mostly unrelated:

- Rows checked: `50,000,000`
- Missing service matches: `0`
- Category mismatches: `40,018,166`

Current downstream effect:

- `category_kpis` reports `active_services = 50,000` for every category.
- A merchant can appear under transaction categories that contradict its service dimension category.
- Merchant/category drilldowns in Power BI will be misleading.

Recommended rule: choose one category source per dashboard page.

- Executive category page: use `interactions.Category` as `transaction_category`.
- Merchant/service page: use `services.Category` as `service_category`.
- Do not join both into one hierarchy unless a correction layer remaps service IDs or category labels.

### Cells 31-32: sample export

The sample is deterministic and useful for prototyping. `SAMPLE_MOD = 1000` produces about `0.1%`, not `1%`, so the file name `interactions_sample_0_1pct.parquet` is accurate.

Risk: because the sample is row-random, it preserves the synthetic flatness. It is fine for performance testing, not for judging realistic chart behavior.

### Cells 35-37: monthly KPIs and charts

Monthly transaction counts are flat after adjusting for days in month. Daily counts average about `136,986`, with coefficient of variation only `0.27%`.

`2024-12-31` is missing, so December looks like a 30-day month. In a monthly line chart, the visible changes mainly reflect 29/30/31-day month length, not business seasonality.

Recommended dashboard fix:

- Add a calendar/date dimension.
- Build weighted daily and monthly marts with a deterministic `demand_weight`.
- Include weekday, seasonality, holiday, campaign, and category-specific factors.
- Show both `raw_transactions` and `adjusted_transactions` during QA, then use adjusted metrics for final storytelling.

### Cells 39-42: category KPIs

Category transaction share can support a simple market-mix story, but it is generated from fixed probabilities. Average amount, completion rate, and active users are almost identical across categories.

Current chart risk:

- Category bars will look plausible only because volumes differ by fixed category weights.
- Category trend lines will be parallel and mechanically proportional.
- Active service counts are invalid because of the category/service mismatch.

Recommended fix:

- Generate category-specific adjusted amount distributions.
- Generate category-specific hourly and weekday curves.
- Replace `active_services` in category KPIs with a corrected metric based on either transaction category or service category, not both.

### Cells 44-50: status, referral, platform, hourly KPIs

These tables are structurally useful but analytically flat:

- Completion rates are approximately `90%` for every category, platform, referral source, and hour.
- Referral sources each contribute about `20%` in every category.
- Platform user agents each contribute about `25%`.
- Hourly counts vary by only about `0.1%` to `0.24%` within categories.

Recommended fix:

- Treat `Referral_Source` as a generated user acquisition source, not a per-transaction truth, or rename it to `Touchpoint_Source`.
- Create platform values conditional on `users.Primary_Device`.
- Generate completion/refund/failure outcomes from category, platform, hour, amount, service rating, and referral source.

### Cell 53: service performance

Service KPIs are not useful for true merchant performance ranking as-is.

Observed pattern:

- 50,000 services.
- Mean transactions per service: exactly `1,000`.
- Service transaction count coefficient of variation: `3.16%`.
- Top services are mostly random noise.
- Transactions per active user per service is almost always `1.0`.

Recommended fix:

- Add merchant popularity tiers or a Pareto/lognormal merchant demand factor.
- Tie service completion rate to `Rating`, category, and platform.
- Do not present current top merchant rankings as business findings.

### Cells 55-63: user lifecycle, cross-sell, and ML features

Lifetime user activity is too uniform for retention or cross-sell analysis:

- Every one of the 2M users has activity.
- Average transactions per user is exactly `25`.
- Median transactions per user is `25`.
- Repeat user rate is `1.0`.
- Multi-service user rate is `1.0`.
- Join-month cohort metrics are almost identical across all 2023 cohorts.
- `83.16%` of users use all 5 categories.

Recommended fix:

- Avoid lifetime `repeat_user_rate` and `multi_service_user_rate` as headline KPIs.
- Redefine repeat users by reporting period, for example users with at least 2 transactions in the selected month.
- Build a generated user lifecycle layer with inactive users, low-activity users, loyal users, dormant users, and high-value users.
- For ML, do not model `is_repeat_user` or `is_multi_service_user` from the current labels because they are nearly constant.

## Field-level trust matrix

| Field or metric | Trust as-is? | Reason | Dashboard guidance |
|---|---:|---|---|
| Transaction UUID | Yes | Unique and complete | Use as transaction key |
| User ID | Yes | Complete FK coverage | Use as user key |
| Service ID | Partially | Complete FK, but category contradiction | Use with caution in merchant pages |
| Timestamp/Date | Partially | Valid, but uniform and missing Dec 31 | Add calendar weighting or adjusted timestamp logic |
| Category | Partially | Useful labels, fixed shares, contradicts service category | Use as transaction category only |
| Amount USD | No | Uniform 5-150 across all groups | Create adjusted amount |
| Status | No | Fixed 90/5/5 everywhere | Create adjusted status |
| Platform user agent | No | Independent of primary device | Create adjusted platform/channel |
| Referral source | No | Uniform per transaction | Create user acquisition source or campaign layer |
| GPS | No | Uniform over globe, many impossible business locations | Replace with synthetic market/city dimension |
| Membership tier | Partially | Plausible 80/15/5 split, but weakly related to behavior | Use after generating behavioral effects |
| Service rating | Partially | Ratings are uniformly distributed 3.0-5.0 | Use only after tying to reliability/volume |

## Recommended correction architecture

Load raw parquet files into BigQuery unchanged:

```text
raw_nova.interactions
raw_nova.users
raw_nova.services
```

Then create curated dbt models:

```text
staging/
  stg_nova__interactions.sql
  stg_nova__users.sql
  stg_nova__services.sql

intermediate/
  int_nova__calendar_factors.sql
  int_nova__user_segments.sql
  int_nova__service_popularity.sql
  int_nova__transaction_adjustments.sql

marts/
  fct_transactions_curated.sql
  dim_users_curated.sql
  dim_services_curated.sql
  dim_markets.sql
  mart_executive_daily.sql
  mart_category_performance.sql
  mart_user_lifecycle.sql
  mart_service_reliability.sql
```

The curated fact table should preserve raw fields and add adjusted fields:

```text
raw_amount_usd
adjusted_amount_usd
raw_status
adjusted_status
transaction_category
service_category
category_match_flag
raw_platform_user_agent
adjusted_platform
raw_referral_source
user_acquisition_source
market_id
demand_weight
```

## Practical fix recipes

### 1. Category and service consistency

Conservative option:

- Keep raw `Service_ID`.
- Rename fact category to `transaction_category`.
- Rename dimension category to `service_category`.
- Add `category_match_flag`.
- Avoid category-to-service drilldown visuals unless filtered to matching rows.

More realistic option:

- Build a deterministic service remapping table by category.
- For mismatched rows, assign an `analytics_service_id` from services in the same transaction category using a hash of `Transaction_UUID`.
- Keep raw `Service_ID` for lineage.

### 2. Time-series realism

Create `demand_weight` from:

- Weekday effect: lower weekends for business-like categories, higher weekends for food/e-commerce.
- Hour-of-day effect: lunch/dinner peaks for food, commute peaks for ride hailing, evening peaks for e-commerce.
- Month effect: holidays and campaign periods.
- Category effect: each category should have a different profile.

Use in marts:

```text
adjusted_transactions = sum(demand_weight)
adjusted_gmv = sum(adjusted_amount_usd * demand_weight)
```

### 3. Amount realism

Replace flat amount charts with `adjusted_amount_usd` generated by category-specific distributions:

- Food Delivery: lower ticket size, lunch/dinner multiplier.
- Grocery: medium-to-high basket size.
- Ride Hailing: distance/time proxy, commute multiplier.
- E-Commerce: long-tailed basket size.
- Digital Wallet: mixed small payments plus larger transfers.

Keep `raw_amount_usd` for audit only.

### 4. Status realism

Generate adjusted status with probabilities driven by:

- Platform/channel.
- Category.
- Hour.
- Amount bucket.
- Service rating.
- User segment.

Example expectations:

- Web may have slightly higher failure than native apps.
- Low-rated services may have higher refund/failure.
- E-commerce may have higher refund rate than food.
- Digital wallet may have different failure behavior than refund behavior.

### 5. Referral and platform realism

Referral should usually be user-level acquisition, not independent on every transaction.

Recommended curated fields:

- `user_acquisition_source` on `dim_users_curated`.
- `touchpoint_source` on transactions if campaign interactions are needed.

Platform should be conditional:

- iOS primary users mostly transact from iOS app or web.
- Android primary users mostly transact from Android app, Lite, or web.
- Web should be available to both.

### 6. Geography

Do not use raw GPS for map visuals. It is uniform across latitude/longitude and will place activity in oceans, poles, and unserved regions.

Create `dim_markets` instead:

- Assign users to 8-20 synthetic cities/markets.
- Give each market realistic lat/long centroids.
- Add market-level demand factors.
- Use jitter only if point maps are necessary.

### 7. User lifecycle

The current lifetime user labels are not analytically useful. Create user segments before dashboarding:

- New/infrequent users.
- Active regular users.
- Power users.
- Dormant users.
- High-value users.
- Category specialists.
- Multi-category adopters.

Use period-based definitions:

- Monthly active users.
- Monthly repeat users.
- 30/60/90-day retained users.
- Users active in current month and previous month.

## Dashboard recommendation

Best final dashboard angle after fixes:

1. Executive performance overview with adjusted daily/monthly volume, GMV, active users, and completion rate.
2. Category performance page using adjusted amount/status/hourly patterns.
3. Reliability page using adjusted status and service rating effects.
4. User lifecycle page using generated/period-based segments.

Avoid as-is:

- Global GPS map.
- Merchant leaderboard based on current `service_kpis`.
- Lifetime repeat user rate.
- Lifetime multi-service user rate.
- Avg amount by category/status/platform from raw `Amount_USD`.
- Completion rate comparisons from raw `Status`.

