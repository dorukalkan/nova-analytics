with service_monthly_health as (
    select *
    from {{ ref('int_service_monthly_health') }}
),

monthly_enriched as (
    select
        month,
        service_id,
        category,
        rating,
        market_id,
        market_name,
        region,
        country_name,
        country_iso2,
        country_iso3,
        world_bank_country_code,
        interaction_count,
        total_amount_usd,
        avg_amount_usd,
        min_amount_usd,
        max_amount_usd,
        completed_count,
        failed_count,
        refunded_count,
        completed_amount_usd,
        failed_amount_usd,
        refunded_amount_usd,
        avg_completed_amount_usd,
        success_rate,
        failure_rate,
        refund_rate,
        amount_success_rate,
        failed_amount_rate,
        refund_amount_rate,
        safe_divide(
            total_amount_usd,
            sum(total_amount_usd) over (partition by month)
        ) as monthly_amount_share,
        rank() over (
            partition by month, category
            order by total_amount_usd desc
        ) as monthly_amount_rank_in_category,
        lag(total_amount_usd) over (
            partition by service_id
            order by month
        ) as previous_month_amount_usd,
        lag(interaction_count) over (
            partition by service_id
            order by month
        ) as previous_month_interaction_count,
        lag(success_rate) over (
            partition by service_id
            order by month
        ) as previous_month_success_rate,
        sum(total_amount_usd) over (
            partition by service_id
            order by month
            rows between 2 preceding and current row
        ) as rolling_3m_amount_usd,
        safe_divide(
            sum(completed_count) over (
                partition by service_id
                order by month
                rows between 2 preceding and current row
            ),
            sum(interaction_count) over (
                partition by service_id
                order by month
                rows between 2 preceding and current row
            )
        ) as rolling_3m_success_rate,
        sum(total_amount_usd) over (
            partition by service_id
            order by month
            rows between 5 preceding and current row
        ) as rolling_6m_amount_usd,
        safe_divide(
            sum(completed_count) over (
                partition by service_id
                order by month
                rows between 5 preceding and current row
            ),
            sum(interaction_count) over (
                partition by service_id
                order by month
                rows between 5 preceding and current row
            )
        ) as rolling_6m_success_rate,
        sum(total_amount_usd) over (
            partition by service_id
            order by month
            rows between 11 preceding and current row
        ) as rolling_12m_amount_usd,
        safe_divide(
            sum(completed_count) over (
                partition by service_id
                order by month
                rows between 11 preceding and current row
            ),
            sum(interaction_count) over (
                partition by service_id
                order by month
                rows between 11 preceding and current row
            )
        ) as rolling_12m_success_rate
    from service_monthly_health
),

service_monthly_performance as (
    select
        month,
        service_id,
        category,
        rating,
        market_id,
        market_name,
        region,
        country_name,
        country_iso2,
        country_iso3,
        world_bank_country_code,
        interaction_count,
        total_amount_usd,
        avg_amount_usd,
        min_amount_usd,
        max_amount_usd,
        completed_count,
        failed_count,
        refunded_count,
        completed_amount_usd,
        failed_amount_usd,
        refunded_amount_usd,
        avg_completed_amount_usd,
        success_rate,
        failure_rate,
        refund_rate,
        amount_success_rate,
        failed_amount_rate,
        refund_amount_rate,
        monthly_amount_share,
        monthly_amount_rank_in_category,
        previous_month_amount_usd,
        total_amount_usd - previous_month_amount_usd as amount_mom_change_usd,
        safe_divide(
            total_amount_usd - previous_month_amount_usd,
            previous_month_amount_usd
        ) as amount_mom_change_pct,
        previous_month_interaction_count,
        safe_divide(
            interaction_count - previous_month_interaction_count,
            previous_month_interaction_count
        ) as interaction_mom_change_pct,
        previous_month_success_rate,
        success_rate - previous_month_success_rate as success_rate_mom_change,
        rolling_3m_amount_usd,
        rolling_3m_success_rate,
        rolling_6m_amount_usd,
        rolling_6m_success_rate,
        rolling_12m_amount_usd,
        rolling_12m_success_rate
    from monthly_enriched
)

select * from service_monthly_performance
