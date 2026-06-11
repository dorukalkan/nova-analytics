with user_service_repeat_behavior as (
    select *
    from {{ ref('int_user_service_repeat_behavior') }}
),

service_repeat_behavior as (
    select
        service_id,
        any_value(category) as category,
        any_value(rating) as rating,
        count(distinct user_id) as user_count,
        count(*) as user_service_pair_count,
        sum(interaction_count) as total_interaction_count,
        countif(is_repeat_user_service) as repeat_user_count,
        sum(repeat_interaction_count) as repeat_interaction_count,
        safe_divide(countif(is_repeat_user_service), count(*)) as repeat_user_rate,
        safe_divide(sum(repeat_interaction_count), sum(interaction_count)) as repeat_interaction_rate,
        avg(interaction_count) as avg_interactions_per_user,
        min(first_interaction_at) as first_interaction_at,
        max(last_interaction_at) as last_interaction_at
    from user_service_repeat_behavior
    group by service_id
)

select * from service_repeat_behavior
