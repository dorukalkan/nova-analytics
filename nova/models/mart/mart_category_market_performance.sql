with service_health as (
    select *
    from {{ ref('int_service_health') }}
),

service_risk as (
    select *
    from {{ ref('int_service_risk') }}
),

category_market_performance as (
    select
        service_health.category,
        service_health.market_id,
        service_health.market_name,
        service_health.region,
        service_health.country_name,
        service_health.country_iso2,
        service_health.country_iso3,
        service_health.world_bank_country_code,
        count(distinct service_health.service_id) as service_count,
        sum(service_health.interaction_count) as total_interaction_count,
        sum(service_health.total_amount_usd) as total_amount_usd,
        safe_divide(
            sum(service_health.total_amount_usd),
            sum(service_health.interaction_count)
        ) as avg_amount_usd,
        sum(service_health.completed_count) as completed_count,
        sum(service_health.failed_count) as failed_count,
        sum(service_health.refunded_count) as refunded_count,
        sum(service_health.completed_amount_usd) as completed_amount_usd,
        sum(service_health.failed_amount_usd) as failed_amount_usd,
        sum(service_health.refunded_amount_usd) as refunded_amount_usd,
        safe_divide(
            sum(service_health.completed_count),
            sum(service_health.interaction_count)
        ) as weighted_success_rate,
        safe_divide(
            sum(service_health.failed_count),
            sum(service_health.interaction_count)
        ) as weighted_failure_rate,
        safe_divide(
            sum(service_health.refunded_count),
            sum(service_health.interaction_count)
        ) as weighted_refund_rate,
        safe_divide(
            sum(service_health.completed_amount_usd),
            sum(service_health.total_amount_usd)
        ) as amount_success_rate,
        safe_divide(
            sum(service_health.failed_amount_usd),
            sum(service_health.total_amount_usd)
        ) as failed_amount_rate,
        safe_divide(
            sum(service_health.refunded_amount_usd),
            sum(service_health.total_amount_usd)
        ) as refund_amount_rate,
        avg(service_health.rating) as avg_rating,
        countif(service_risk.risk_segment = 'Critical') as critical_service_count,
        countif(service_risk.risk_segment = 'High Risk') as high_risk_service_count,
        countif(service_risk.risk_segment = 'Monitor') as monitor_service_count,
        countif(service_risk.risk_segment = 'Healthy') as healthy_service_count
    from service_health
    left join service_risk
        on service_health.service_id = service_risk.service_id
    group by
        service_health.category,
        service_health.market_id,
        service_health.market_name,
        service_health.region,
        service_health.country_name,
        service_health.country_iso2,
        service_health.country_iso3,
        service_health.world_bank_country_code
)

select * from category_market_performance
