select
    sum(transactions) as transactions,
    sum(completed_transactions + failed_transactions + refunded_transactions) as status_total
from {{ ref('mart_geo_market_category_day_features') }}
having transactions != status_total
