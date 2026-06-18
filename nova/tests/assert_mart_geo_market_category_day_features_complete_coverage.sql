with coverage as (
    select
        count(*) as row_count,
        count(distinct market_id) as market_count,
        count(distinct category) as category_count,
        count(distinct order_date) as date_count,
        min(order_date) as min_date,
        max(order_date) as max_date
    from {{ ref('mart_geo_market_category_day_features') }}
)

select *
from coverage
where row_count != 29280
    or market_count != 16
    or category_count != 5
    or date_count != 366
    or min_date != date '2024-01-01'
    or max_date != date '2024-12-31'
