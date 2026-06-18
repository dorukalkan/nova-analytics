select
    market_id,
    category,
    order_date,
    count(*) as row_count
from {{ ref('mart_geo_market_category_day_features') }}
group by 1, 2, 3
having count(*) > 1
