with service_interactions as (
    select *
    from {{ ref('int_service_interactions') }}
),

service_monthly_health as (
    select
        date_trunc(date(timestamp), month) as month,
        service_id,
        any_value(category) as category,
        any_value(rating) as rating,
        count(*) as interaction_count,
        countif(status = 'Completed') as completed_count,
        countif(status = 'Failed') as failed_count,
        countif(status = 'Refunded') as refunded_count,
        safe_divide(countif(status = 'Completed'), count(*)) as success_rate,
        safe_divide(countif(status = 'Failed'), count(*)) as failure_rate,
        safe_divide(countif(status = 'Refunded'), count(*)) as refund_rate
    from service_interactions
    group by
        month,
        service_id
)

select * from service_monthly_health
