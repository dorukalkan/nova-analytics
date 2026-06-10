with source as (
select *
from {{ source('raw', 'nova_users') }}
),
cleaned as (
select
    User_ID as user_id,
    Join_Date as join_date,
    Membership_Tier as membership_tier,
    Primary_Device as primary_device,
    Market_ID as market_id,
    Market_Name as market_name,
    Region as region,
    Acquisition_Source as acquisition_source,
    User_Segment as user_segment,
    Lifecycle_Segment as lifecycle_segment
from source
)

select * from cleaned