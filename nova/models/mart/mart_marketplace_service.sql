with service_health as (
    select *
    from {{ ref('int_service_health') }}
),

service_risk as (
    select *
    from {{ ref('int_service_risk') }}
),

marketplace_service as (
    select
        service_health.service_id,
        service_health.category,
        service_health.rating,
        service_health.interaction_count,
        service_health.completed_count,
        service_health.failed_count,
        service_health.refunded_count,
        service_health.success_rate,
        service_health.failure_rate,
        service_health.refund_rate,
        service_risk.risk_segment,
        case service_risk.risk_segment
            when 'Critical' then 1
            when 'High Risk' then 2
            when 'Monitor' then 3
            when 'Healthy' then 4
        end as risk_priority
    from service_health
    left join service_risk
        on service_health.service_id = service_risk.service_id
)

select * from marketplace_service
