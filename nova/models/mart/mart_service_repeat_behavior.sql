with user_service_repeat_behavior as (
    select *
    from {{ ref('int_user_service_repeat_behavior') }}
),

service_repeat_amounts as (
    select
        service_id,
        sum(if(interaction_sequence > 1, amount, 0)) as repeat_amount_usd
    from (
        select
            service_id,
            amount,
            row_number() over (
                partition by user_id, service_id
                order by timestamp, transaction_uuid
            ) as interaction_sequence
        from {{ ref('int_service_interactions') }}
    )
    group by service_id
),

service_repeat_behavior as (
    select
        user_service_repeat_behavior.service_id,
        any_value(user_service_repeat_behavior.category) as category,
        any_value(user_service_repeat_behavior.rating) as rating,
        any_value(user_service_repeat_behavior.market_id) as market_id,
        any_value(user_service_repeat_behavior.market_name) as market_name,
        any_value(user_service_repeat_behavior.region) as region,
        any_value(user_service_repeat_behavior.country_name) as country_name,
        any_value(user_service_repeat_behavior.country_iso2) as country_iso2,
        any_value(user_service_repeat_behavior.country_iso3) as country_iso3,
        any_value(user_service_repeat_behavior.world_bank_country_code) as world_bank_country_code,
        count(distinct user_service_repeat_behavior.user_id) as user_count,
        count(*) as user_service_pair_count,
        sum(user_service_repeat_behavior.interaction_count) as total_interaction_count,
        sum(user_service_repeat_behavior.total_amount_usd) as total_amount_usd,
        safe_divide(
            sum(user_service_repeat_behavior.total_amount_usd),
            sum(user_service_repeat_behavior.interaction_count)
        ) as avg_amount_usd,
        safe_divide(
            sum(user_service_repeat_behavior.total_amount_usd),
            count(distinct user_service_repeat_behavior.user_id)
        ) as avg_amount_per_user,
        any_value(service_repeat_amounts.repeat_amount_usd) as repeat_amount_usd,
        safe_divide(
            any_value(service_repeat_amounts.repeat_amount_usd),
            sum(user_service_repeat_behavior.total_amount_usd)
        ) as repeat_amount_rate,
        countif(user_service_repeat_behavior.is_repeat_user_service) as repeat_user_count,
        sum(user_service_repeat_behavior.repeat_interaction_count) as repeat_interaction_count,
        safe_divide(countif(user_service_repeat_behavior.is_repeat_user_service), count(*)) as repeat_user_rate,
        safe_divide(
            sum(user_service_repeat_behavior.repeat_interaction_count),
            sum(user_service_repeat_behavior.interaction_count)
        ) as repeat_interaction_rate,
        safe_divide(
            sum(if(
                user_service_repeat_behavior.is_repeat_user_service,
                user_service_repeat_behavior.total_amount_usd,
                0
            )),
            countif(user_service_repeat_behavior.is_repeat_user_service)
        ) as amount_per_repeat_user,
        safe_divide(
            sum(if(
                user_service_repeat_behavior.is_repeat_user_service,
                user_service_repeat_behavior.total_amount_usd,
                0
            )),
            sum(user_service_repeat_behavior.total_amount_usd)
        ) as repeat_user_amount_share,
        avg(user_service_repeat_behavior.interaction_count) as avg_interactions_per_user,
        min(user_service_repeat_behavior.first_interaction_at) as first_interaction_at,
        max(user_service_repeat_behavior.last_interaction_at) as last_interaction_at
    from user_service_repeat_behavior
    left join service_repeat_amounts
        on user_service_repeat_behavior.service_id = service_repeat_amounts.service_id
    group by user_service_repeat_behavior.service_id
)

select * from service_repeat_behavior
