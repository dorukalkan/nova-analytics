select
    market_id,
    category,
    count(*) as row_count
from {{ ref('int_geo_service_supply_by_market_category') }}
group by 1, 2
having count(*) > 1
