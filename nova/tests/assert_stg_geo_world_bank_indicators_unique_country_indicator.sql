select
    country_iso3,
    indicator_code,
    count(*) as row_count
from {{ ref('stg_geo_world_bank_indicators') }}
group by 1, 2
having count(*) > 1
