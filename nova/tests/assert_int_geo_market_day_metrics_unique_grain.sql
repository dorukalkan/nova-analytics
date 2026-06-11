select
    market_id,
    order_date,
    count(*) as row_count
from {{ ref('int_geo_market_day_metrics') }}
group by 1, 2
having count(*) > 1
