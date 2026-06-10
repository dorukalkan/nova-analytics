with source as (
select *
from {{ source('raw', 'nova_services') }}
),
cleaned as (
select
Service_ID as service_id,
Merchant_Name as merchant_name,
Category as category,
Rating as rating,
Market_ID as market_id,
Market_Name as market_name,
Region as region,
Service_Tier as service_tier,
Popularity_Score as popularity_score
from source
)

select * from cleaned



