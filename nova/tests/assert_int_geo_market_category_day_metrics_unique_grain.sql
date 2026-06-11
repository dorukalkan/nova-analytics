select
    market_id,
    category,
    order_date,
    count(*) as row_count
from {{ ref('int_geo_market_category_day_metrics') }}
group by 1, 2, 3
having count(*) > 1
