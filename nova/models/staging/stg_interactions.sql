with source as (
select *
from {{ source('raw', 'nova_interactions') }}
),
cleaned as (
select
    Transaction_UUID as transaction_id,
    User_ID as user_id,
    Service_ID as service_id,
    Category as category,
    Amount_USD as amount,
    Status as status,
    Platform_User_Agent as platform_user_agent,
    Referral_Source as referral_source,
    GPS_Lat as gps_lat,
    GPS_Long as gps_long,
    Timestamp_dt as timestamp,
    DATE(Timestamp_dt) AS order_date,
    TIME(Timestamp_dt) AS order_time,
    Market_ID as market_id,
    Market_Name as market_name,
    Region as region,
    Acquisition_Source as acquisition_source,
    User_Segment as user_segment,
    Lifecycle_Segment as lifecycle_segment,
    Service_Tier as service_tier,
    Is_Promo_Period as is_promo_period
from source
)

select * from cleaned
