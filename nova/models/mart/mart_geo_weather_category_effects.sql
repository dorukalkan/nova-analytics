with features as (
    select *
    from {{ ref('mart_geo_market_category_day_features') }}
),

market_days as (
    select distinct
        market_id,
        market_name,
        nova_region,
        country_iso3,
        country_name,
        order_date,
        year_month,
        temperature_2m_mean_c,
        precipitation_sum_mm,
        rain_sum_mm,
        wind_speed_10m_max_kmh,
        is_rain_day
    from features
),

weather_thresholds as (
    select
        market_days.*,
        percentile_cont(temperature_2m_mean_c, 0.10) over (
            partition by market_id, year_month
        ) as market_month_temp_p10_c,
        percentile_cont(temperature_2m_mean_c, 0.90) over (
            partition by market_id, year_month
        ) as market_month_temp_p90_c,
        percentile_cont(precipitation_sum_mm, 0.90) over (
            partition by market_id
        ) as market_precip_p90_mm,
        percentile_cont(wind_speed_10m_max_kmh, 0.90) over (
            partition by market_id
        ) as market_wind_p90_kmh
    from market_days
),

flagged_market_days as (
    select
        *,
        (
            coalesce(precipitation_sum_mm, 0) >= greatest(coalesce(market_precip_p90_mm, 0), 8.0)
            or temperature_2m_mean_c >= market_month_temp_p90_c
            or temperature_2m_mean_c <= market_month_temp_p10_c
            or coalesce(wind_speed_10m_max_kmh, 0) >= greatest(coalesce(market_wind_p90_kmh, 0), 28.0)
        ) as is_bad_weather_day
    from weather_thresholds
),

features_with_weather_flags as (
    select
        features.*,
        flagged_market_days.is_bad_weather_day
    from features
    left join flagged_market_days
        on features.market_id = flagged_market_days.market_id
        and features.order_date = flagged_market_days.order_date
),

market_category_effects as (
    select
        'Market' as weather_effect_scope,
        market_id,
        market_name,
        nova_region,
        country_iso3,
        country_name,
        category,
        count(*) as observed_days,
        countif(is_bad_weather_day) as bad_weather_days,
        countif(not is_bad_weather_day) as normal_weather_days,
        countif(is_rain_day) as rain_days,
        countif(not is_rain_day) as non_rain_days,
        sum(transactions) as total_transactions,
        sum(gmv_usd) as total_gmv_usd,
        avg(transactions) as avg_daily_transactions,
        avg(gmv_usd) as avg_daily_gmv_usd,
        avg(if(is_bad_weather_day, transactions, null)) as avg_bad_weather_transactions,
        avg(if(not is_bad_weather_day, transactions, null)) as avg_normal_weather_transactions,
        avg(if(is_bad_weather_day, gmv_usd, null)) as avg_bad_weather_gmv_usd,
        avg(if(not is_bad_weather_day, gmv_usd, null)) as avg_normal_weather_gmv_usd,
        avg(if(is_bad_weather_day, completion_rate, null)) as avg_bad_weather_completion_rate,
        avg(if(not is_bad_weather_day, completion_rate, null)) as avg_normal_weather_completion_rate,
        avg(if(is_rain_day, transactions, null)) as avg_rain_day_transactions,
        avg(if(not is_rain_day, transactions, null)) as avg_non_rain_day_transactions,
        avg(if(is_rain_day, gmv_usd, null)) as avg_rain_day_gmv_usd,
        avg(if(not is_rain_day, gmv_usd, null)) as avg_non_rain_day_gmv_usd
    from features_with_weather_flags
    group by 1, 2, 3, 4, 5, 6, 7
),

all_market_category_effects as (
    select
        'All Markets' as weather_effect_scope,
        cast(null as int64) as market_id,
        'All Markets' as market_name,
        'All Regions' as nova_region,
        cast(null as string) as country_iso3,
        'All Countries' as country_name,
        category,
        count(*) as observed_days,
        countif(is_bad_weather_day) as bad_weather_days,
        countif(not is_bad_weather_day) as normal_weather_days,
        countif(is_rain_day) as rain_days,
        countif(not is_rain_day) as non_rain_days,
        sum(transactions) as total_transactions,
        sum(gmv_usd) as total_gmv_usd,
        avg(transactions) as avg_daily_transactions,
        avg(gmv_usd) as avg_daily_gmv_usd,
        avg(if(is_bad_weather_day, transactions, null)) as avg_bad_weather_transactions,
        avg(if(not is_bad_weather_day, transactions, null)) as avg_normal_weather_transactions,
        avg(if(is_bad_weather_day, gmv_usd, null)) as avg_bad_weather_gmv_usd,
        avg(if(not is_bad_weather_day, gmv_usd, null)) as avg_normal_weather_gmv_usd,
        avg(if(is_bad_weather_day, completion_rate, null)) as avg_bad_weather_completion_rate,
        avg(if(not is_bad_weather_day, completion_rate, null)) as avg_normal_weather_completion_rate,
        avg(if(is_rain_day, transactions, null)) as avg_rain_day_transactions,
        avg(if(not is_rain_day, transactions, null)) as avg_non_rain_day_transactions,
        avg(if(is_rain_day, gmv_usd, null)) as avg_rain_day_gmv_usd,
        avg(if(not is_rain_day, gmv_usd, null)) as avg_non_rain_day_gmv_usd
    from features_with_weather_flags
    group by 1, 2, 3, 4, 5, 6, 7
),

combined as (
    select * from market_category_effects
    union all
    select * from all_market_category_effects
),

with_effects as (
    select
        *,
        safe_divide(
            avg_bad_weather_transactions - avg_normal_weather_transactions,
            nullif(avg_normal_weather_transactions, 0)
        ) as bad_weather_transaction_lift_pct,
        safe_divide(
            avg_bad_weather_gmv_usd - avg_normal_weather_gmv_usd,
            nullif(avg_normal_weather_gmv_usd, 0)
        ) as bad_weather_gmv_lift_pct,
        avg_bad_weather_completion_rate - avg_normal_weather_completion_rate as bad_weather_completion_rate_delta,
        safe_divide(
            avg_rain_day_transactions - avg_non_rain_day_transactions,
            nullif(avg_non_rain_day_transactions, 0)
        ) as rain_transaction_lift_pct,
        safe_divide(
            avg_rain_day_gmv_usd - avg_non_rain_day_gmv_usd,
            nullif(avg_non_rain_day_gmv_usd, 0)
        ) as rain_gmv_lift_pct
    from combined
)

select
    concat(
        weather_effect_scope,
        '|',
        coalesce(cast(market_id as string), 'all'),
        '|',
        category
    ) as weather_effect_id,
    *,
    case
        when bad_weather_days < 10 or normal_weather_days < 10 then 'Limited comparison'
        when bad_weather_transaction_lift_pct >= 0.10 then 'Bad-weather positive demand'
        when bad_weather_transaction_lift_pct <= -0.10 then 'Bad-weather negative demand'
        else 'Low bad-weather sensitivity'
    end as bad_weather_sensitivity_segment
from with_effects
