
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
        count(*) as interaction_count,
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
