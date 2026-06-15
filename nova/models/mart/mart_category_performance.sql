with category_health as (
    select *
    from {{ ref('int_category_health') }}
),

service_health as (
    select *
    from {{ ref('int_service_health') }}
),

service_risk as (
    select *
    from {{ ref('int_service_risk') }}
),

category_rollup as (
    select
        service_health.category,
        sum(service_health.completed_count) as completed_count,
        sum(service_health.failed_count) as failed_count,
        sum(service_health.refunded_count) as refunded_count,
        sum(service_health.completed_amount_usd) as completed_amount_usd,
        sum(service_health.failed_amount_usd) as failed_amount_usd,
        sum(service_health.refunded_amount_usd) as refunded_amount_usd,
        countif(service_risk.risk_segment = 'Critical') as critical_service_count,
        countif(service_risk.risk_segment = 'High Risk') as high_risk_service_count,
        countif(service_risk.risk_segment = 'Monitor') as monitor_service_count,
        countif(service_risk.risk_segment = 'Healthy') as healthy_service_count
    from service_health
    left join service_risk
        on service_health.service_id = service_risk.service_id
    group by service_health.category
),

category_performance as (
    select
        category_health.category,
        category_health.service_count,
        category_health.total_interaction_count,
        category_health.total_amount_usd,
        category_health.avg_amount_usd,
        category_health.avg_success_rate,
        category_health.avg_failure_rate,
        category_health.avg_refund_rate,
        category_health.avg_rating,
        category_rollup.completed_count,
        category_rollup.failed_count,
        category_rollup.refunded_count,
        category_rollup.completed_amount_usd,
        category_rollup.failed_amount_usd,
        category_rollup.refunded_amount_usd,
        safe_divide(category_rollup.completed_count, category_health.total_interaction_count) as weighted_success_rate,
        safe_divide(category_rollup.failed_count, category_health.total_interaction_count) as weighted_failure_rate,
        safe_divide(category_rollup.refunded_count, category_health.total_interaction_count) as weighted_refund_rate,
        safe_divide(category_rollup.completed_amount_usd, category_health.total_amount_usd) as amount_success_rate,
        safe_divide(category_rollup.failed_amount_usd, category_health.total_amount_usd) as failed_amount_rate,
        safe_divide(category_rollup.refunded_amount_usd, category_health.total_amount_usd) as refund_amount_rate,
        safe_divide(
            category_health.total_amount_usd,
            sum(category_health.total_amount_usd) over ()
        ) as category_amount_share,
        safe_divide(category_health.total_amount_usd, category_health.service_count) as amount_per_service,
        safe_divide(category_health.total_amount_usd, category_rollup.completed_count) as amount_per_successful_interaction,
        category_rollup.critical_service_count,
        category_rollup.high_risk_service_count,
        category_rollup.monitor_service_count,
        category_rollup.healthy_service_count
    from category_health
    left join category_rollup
        on category_health.category = category_rollup.category
)

select * from category_performance
