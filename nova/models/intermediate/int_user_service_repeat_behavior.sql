
with service_interactions as (
    select *
    from {{ ref('int_service_interactions') }}
),

user_service_repeat_behavior as (
    select
        user_id,
        service_id,
        any_value(category) as category,
        any_value(rating) as rating,
        any_value(market_id) as market_id,
        any_value(market_name) as market_name,
        any_value(region) as region,
        any_value(country_name) as country_name,
        any_value(country_iso2) as country_iso2,
        any_value(country_iso3) as country_iso3,
        any_value(world_bank_country_code) as world_bank_country_code,
        count(*) as interaction_count,
        sum(amount) as total_amount_usd,
        avg(amount) as avg_amount_usd,
        min(timestamp) as first_interaction_at,
        max(timestamp) as last_interaction_at,
        count(*) > 1 as is_repeat_user_service,
        greatest(count(*) - 1, 0) as repeat_interaction_count
    from service_interactions
    group by
        user_id,
        service_id
)

select * from user_service_repeat_behavior
