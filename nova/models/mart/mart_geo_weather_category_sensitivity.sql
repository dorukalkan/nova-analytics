with features as (
    select *
    from {{ ref('mart_geo_market_category_day_features') }}
),

aggregated as (
    select
        market_id,
        market_name,
        nova_region,
        country_iso3,
        country_name,
        category,
        count(*) as observed_days,
        countif(is_rain_day) as rain_days,
        countif(not is_rain_day) as non_rain_days,
        sum(transactions) as total_transactions,
        sum(gmv_usd) as total_gmv_usd,
        avg(transactions) as avg_daily_transactions,
        avg(gmv_usd) as avg_daily_gmv_usd,
        avg(if(is_rain_day, transactions, null)) as avg_rain_day_transactions,
        avg(if(not is_rain_day, transactions, null)) as avg_non_rain_day_transactions,
        avg(if(is_rain_day, gmv_usd, null)) as avg_rain_day_gmv_usd,
        avg(if(not is_rain_day, gmv_usd, null)) as avg_non_rain_day_gmv_usd,
        avg(if(is_rain_day, completion_rate, null)) as avg_rain_day_completion_rate,
        avg(if(not is_rain_day, completion_rate, null)) as avg_non_rain_day_completion_rate,
        avg(temperature_2m_mean_c) as avg_temperature_2m_mean_c,
        avg(precipitation_sum_mm) as avg_precipitation_sum_mm,
        corr(cast(precipitation_sum_mm as float64), cast(transactions as float64)) as precipitation_transaction_corr,
        corr(cast(temperature_2m_mean_c as float64), cast(transactions as float64)) as temperature_transaction_corr
    from features
    group by 1, 2, 3, 4, 5, 6
),

with_lift as (
    select
        *,
        safe_divide(
            avg_rain_day_transactions - avg_non_rain_day_transactions,
            nullif(avg_non_rain_day_transactions, 0)
        ) as rain_transaction_lift_pct,
        safe_divide(
            avg_rain_day_gmv_usd - avg_non_rain_day_gmv_usd,
            nullif(avg_non_rain_day_gmv_usd, 0)
        ) as rain_gmv_lift_pct,
        avg_rain_day_completion_rate - avg_non_rain_day_completion_rate as rain_completion_rate_delta
    from aggregated
)

select
    *,
    rank() over (
        partition by category
        order by abs(coalesce(rain_transaction_lift_pct, 0)) desc
    ) as category_weather_sensitivity_rank,
    case
        when rain_days < 10 or non_rain_days < 10 then 'Limited comparison'
        when rain_transaction_lift_pct >= 0.10 then 'Rain-positive demand'
        when rain_transaction_lift_pct <= -0.10 then 'Rain-negative demand'
        else 'Low rain sensitivity'
    end as rain_sensitivity_segment
from with_lift
