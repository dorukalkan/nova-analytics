select
    market_id,
    weather_date,
    count(*) as row_count
from {{ ref('stg_geo_weather_daily') }}
group by 1, 2
having count(*) > 1
