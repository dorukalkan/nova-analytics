with source as (
select *
from {{ source('raw', 'nova_markets') }}
),
cleaned as (
select
    Market_ID as market_id,
    Market_Name as market_name,
    Region as region,
    Latitude as latitude,
    Longitude as longitude,
    Market_Weight as market_weight,
    Growth_Multiplier as growth_multiplier,
    IOS_Share as ios_share
from source
)

select * from cleaned
