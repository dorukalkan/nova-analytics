with service_health as (
    select *
    from {{ ref('int_service_health') }}
),

category_health as (
    select
        category,
        count(distinct service_id) as service_count,
        sum(interaction_count) as total_interaction_count,
        avg(success_rate) as avg_success_rate,
        avg(failure_rate) as avg_failure_rate,
        avg(refund_rate) as avg_refund_rate,
        avg(rating) as avg_rating
    from service_health
    group by category
)

select * from category_health
