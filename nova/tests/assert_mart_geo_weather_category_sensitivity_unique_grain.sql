select
    market_id,
    category,
    count(*) as row_count
from {{ ref('mart_geo_weather_category_sensitivity') }}
group by 1, 2
having count(*) > 1
