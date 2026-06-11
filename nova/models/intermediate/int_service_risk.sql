with service_health as (
    select *
    from {{ ref('int_service_health') }}
),

service_risk as (
    select
        service_id,
        category,
        rating,
        success_rate,
        failure_rate,
        refund_rate,
        case
            when success_rate < 0.80
                or failure_rate >= 0.15
                or refund_rate >= 0.10
                or rating < 3.4
                then 'Critical'
            when success_rate < 0.87
                or failure_rate >= 0.10
                or refund_rate >= 0.07
                or rating < 3.8
                then 'High Risk'
            when success_rate < 0.92
                or failure_rate >= 0.06
                or refund_rate >= 0.04
                or rating < 4.1
                then 'Monitor'
            else 'Healthy'
        end as risk_segment
    from service_health
)

select * from service_risk
