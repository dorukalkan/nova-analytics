select
    count(*) as rows,
    count(distinct market_id) as markets,
    count(distinct category) as categories,
    count(distinct order_date) as dates,
    min(order_date) as min_date,
    max(order_date) as max_date
from {{ ref('mart_geo_market_category_day_features') }}
having rows != 29280
    or markets != 16
    or categories != 5
    or dates != 366
    or min_date != date '2024-01-01'
    or max_date != date '2024-12-31'
