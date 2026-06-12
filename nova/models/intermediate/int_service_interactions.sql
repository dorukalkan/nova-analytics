with interactions as (
    select *
    from {{ref('stg_interactions')}}
),

services as (
    select *
    from {{ ref('stg_services') }}
),

service_interactions as (
    select
        interactions.transaction_id as transaction_uuid,
        interactions.user_id,
        interactions.service_id,
        interactions.category,
        services.rating,
        interactions.status,
        interactions.timestamp,
        interactions.order_date,
        interactions.order_time,
        interactions.amount,
        interactions.acquisition_source
    from interactions
    left join services
        on interactions.service_id = services.service_id
)

select * from service_interactions
