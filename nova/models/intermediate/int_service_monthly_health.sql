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
        min(amount) as min_amount_usd,
        max(amount) as max_amount_usd,
        countif(status = 'Completed') as completed_count,
        countif(status = 'Failed') as failed_count,
        countif(status = 'Refunded') as refunded_count,
        sum(if(status = 'Completed', amount, 0)) as completed_amount_usd,
        sum(if(status = 'Failed', amount, 0)) as failed_amount_usd,
        sum(if(status = 'Refunded', amount, 0)) as refunded_amount_usd,
        avg(if(status = 'Completed', amount, null)) as avg_completed_amount_usd,
        safe_divide(countif(status = 'Completed'), count(*)) as success_rate,
        safe_divide(countif(status = 'Failed'), count(*)) as failure_rate,
        safe_divide(countif(status = 'Refunded'), count(*)) as refund_rate,
        safe_divide(sum(if(status = 'Completed', amount, 0)), sum(amount)) as amount_success_rate,
        safe_divide(sum(if(status = 'Failed', amount, 0)), sum(amount)) as failed_amount_rate,
        safe_divide(sum(if(status = 'Refunded', amount, 0)), sum(amount)) as refund_amount_rate
    from service_interactions
    group by
        month,
        service_id
)

select * from service_monthly_health
