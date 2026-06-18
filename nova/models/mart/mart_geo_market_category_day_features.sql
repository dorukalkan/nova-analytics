with spine as (
    select *
    from {{ ref('int_geo_market_category_spine') }}
),

metrics as (
    select *
    from {{ ref('int_geo_market_category_day_metrics') }}
),

market_context as (
    select *
    from {{ ref('int_geo_market_context') }}
),

calendar as (
    select *
    from {{ ref('int_geo_date_spine') }}
),

weather as (
    select *
    from {{ ref('stg_geo_weather_daily') }}
),

service_supply as (
    select *
    from {{ ref('int_geo_service_supply_by_market_category') }}
),

base_features as (
    select
        spine.market_id,
        spine.market_name,
        spine.region as nova_region,
        market_context.latitude,
        market_context.longitude,
        market_context.market_weight,
        market_context.growth_multiplier,
        market_context.ios_share as configured_ios_share,
        market_context.country_name,
        market_context.country_iso2,
        market_context.country_iso3,
        market_context.country_region,
        market_context.country_subregion,
        market_context.currency_code,
        market_context.population_total,
        market_context.gdp_per_capita_current_usd,
        market_context.urban_population_pct,
        market_context.internet_users_pct,
        market_context.mobile_subscriptions_per_100_people,

        spine.category,
        spine.order_date,
        calendar.year,
        calendar.quarter,
        calendar.month,
        calendar.year_month,
        calendar.day_of_week,
        calendar.day_name,
        calendar.is_weekend,

        coalesce(metrics.transactions, 0) as transactions,
        coalesce(metrics.gmv_usd, 0) as gmv_usd,
        coalesce(metrics.avg_transaction_amount_usd, 0) as avg_transaction_amount_usd,
        coalesce(metrics.active_users, 0) as active_users,
        coalesce(metrics.active_services_with_transactions, 0) as active_services_with_transactions,
        coalesce(metrics.completed_transactions, 0) as completed_transactions,
        coalesce(metrics.failed_transactions, 0) as failed_transactions,
        coalesce(metrics.refunded_transactions, 0) as refunded_transactions,
        coalesce(metrics.completion_rate, 0) as completion_rate,
        coalesce(metrics.failed_rate, 0) as failed_rate,
        coalesce(metrics.refunded_rate, 0) as refunded_rate,
        coalesce(metrics.promo_transactions, 0) as promo_transactions,
        coalesce(metrics.promo_share, 0) as promo_share,
        coalesce(metrics.head_tier_transactions, 0) as head_tier_transactions,
        coalesce(metrics.mid_tier_transactions, 0) as mid_tier_transactions,
        coalesce(metrics.long_tail_tier_transactions, 0) as long_tail_tier_transactions,
        coalesce(metrics.head_tier_transaction_share, 0) as head_tier_transaction_share,
        coalesce(metrics.mid_tier_transaction_share, 0) as mid_tier_transaction_share,
        coalesce(metrics.long_tail_tier_transaction_share, 0) as long_tail_tier_transaction_share,
        coalesce(metrics.ios_transactions, 0) as ios_transactions,
        coalesce(metrics.android_transactions, 0) as android_transactions,
        coalesce(metrics.lite_transactions, 0) as lite_transactions,
        coalesce(metrics.web_transactions, 0) as web_transactions,
        coalesce(metrics.ios_transaction_share, 0) as ios_transaction_share,
        coalesce(metrics.android_transaction_share, 0) as android_transaction_share,
        coalesce(metrics.lite_transaction_share, 0) as lite_transaction_share,
        coalesce(metrics.web_transaction_share, 0) as web_transaction_share,

        service_supply.active_services,
        service_supply.avg_service_rating,
        service_supply.avg_popularity_score,
        service_supply.head_services,
        service_supply.mid_services,
        service_supply.long_tail_services,
        service_supply.head_service_share,
        service_supply.mid_service_share,
        service_supply.long_tail_service_share,

        weather.weather_code,
        weather.temperature_2m_mean_c,
        weather.temperature_2m_max_c,
        weather.temperature_2m_min_c,
        weather.apparent_temperature_mean_c,
        weather.precipitation_sum_mm,
        weather.rain_sum_mm,
        weather.precipitation_hours,
        weather.wind_speed_10m_max_kmh,
        weather.is_rain_day,
        case
            when weather.temperature_2m_mean_c < 10 then 'cold'
            when weather.temperature_2m_mean_c < 20 then 'mild'
            when weather.temperature_2m_mean_c < 30 then 'warm'
            else 'hot'
        end as temperature_band,
        case
            when coalesce(weather.precipitation_sum_mm, 0) = 0 then 'none'
            when weather.precipitation_sum_mm < 5 then 'light'
            when weather.precipitation_sum_mm < 20 then 'moderate'
            else 'heavy'
        end as precipitation_band
    from spine
    left join metrics
        on spine.market_id = metrics.market_id
        and spine.category = metrics.category
        and spine.order_date = metrics.order_date
    left join market_context
        on spine.market_id = market_context.market_id
    left join calendar
        on spine.order_date = calendar.order_date
    left join weather
        on spine.market_id = weather.market_id
        and spine.order_date = weather.weather_date
    left join service_supply
        on spine.market_id = service_supply.market_id
        and spine.category = service_supply.category
),

with_thresholds as (
    select
        base_features.*,
        avg(transactions) over (
            partition by market_id, category
        ) as avg_market_category_daily_transactions,
        percentile_cont(transactions, 0.75) over (
            partition by market_id, category
        ) as p75_market_category_daily_transactions
    from base_features
)

select
    *,
    transactions >= p75_market_category_daily_transactions as is_high_demand_day,
    safe_divide(transactions, nullif(avg_market_category_daily_transactions, 0)) as demand_index_vs_market_category_avg
from with_thresholds
