with interactions as (
    select *
    from {{ref('stg_interactions')}}
),

services as (
    select *
    from {{ ref('int_services_enriched') }}
),

service_interactions as (
    select
        interactions.transaction_id as transaction_uuid,
        interactions.user_id,
        interactions.service_id,
        interactions.category,
        services.rating,
        services.market_id,
        services.market_name,
        services.region,
        services.country_name,
        services.country_iso2,
        services.country_iso3,
        services.world_bank_country_code,
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
