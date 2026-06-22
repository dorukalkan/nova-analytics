with market_opportunity as (
    select *
    from {{ ref('mart_geo_market_opportunity') }}
),

market_category_day_features as (
    select *
    from {{ ref('mart_geo_market_category_day_features') }}
),

weather_sensitivity as (
    select *
    from {{ ref('mart_geo_weather_category_sensitivity') }}
),

category_mix as (
    select
        market_id,
        safe_divide(sum(if(category = 'Food Delivery', transactions, 0)), nullif(sum(transactions), 0)) as food_delivery_transaction_share,
        safe_divide(sum(if(category = 'Ride Hailing', transactions, 0)), nullif(sum(transactions), 0)) as ride_hailing_transaction_share,
        safe_divide(sum(if(category = 'E-Commerce', transactions, 0)), nullif(sum(transactions), 0)) as e_commerce_transaction_share,
        safe_divide(sum(if(category = 'Grocery', transactions, 0)), nullif(sum(transactions), 0)) as grocery_transaction_share,
        safe_divide(sum(if(category = 'Digital Wallet', transactions, 0)), nullif(sum(transactions), 0)) as digital_wallet_transaction_share,
        safe_divide(sum(if(category = 'Food Delivery', gmv_usd, 0)), nullif(sum(gmv_usd), 0)) as food_delivery_gmv_share,
        safe_divide(sum(if(category = 'Ride Hailing', gmv_usd, 0)), nullif(sum(gmv_usd), 0)) as ride_hailing_gmv_share,
        safe_divide(sum(if(category = 'E-Commerce', gmv_usd, 0)), nullif(sum(gmv_usd), 0)) as e_commerce_gmv_share,
        safe_divide(sum(if(category = 'Grocery', gmv_usd, 0)), nullif(sum(gmv_usd), 0)) as grocery_gmv_share,
        safe_divide(sum(if(category = 'Digital Wallet', gmv_usd, 0)), nullif(sum(gmv_usd), 0)) as digital_wallet_gmv_share
    from market_category_day_features
    group by market_id
),

daily_weather_context as (
    select
        market_id,
        avg(temperature_2m_mean_c) as avg_temperature_2m_mean_c,
        avg(precipitation_sum_mm) as avg_precipitation_sum_mm,
        avg(rain_sum_mm) as avg_rain_sum_mm,
        avg(precipitation_hours) as avg_precipitation_hours,
        avg(wind_speed_10m_max_kmh) as avg_wind_speed_10m_max_kmh,
        safe_divide(countif(is_rain_day), count(*)) as rain_day_share
    from market_category_day_features
    group by market_id
),

weather_sensitivity_by_market as (
    select
        market_id,
        avg(rain_transaction_lift_pct) as avg_rain_transaction_lift_pct,
        avg(rain_gmv_lift_pct) as avg_rain_gmv_lift_pct,
        max(abs(coalesce(rain_transaction_lift_pct, 0))) as max_abs_rain_transaction_lift_pct,
        max(abs(coalesce(rain_gmv_lift_pct, 0))) as max_abs_rain_gmv_lift_pct,
        avg(precipitation_transaction_corr) as avg_precipitation_transaction_corr,
        avg(temperature_transaction_corr) as avg_temperature_transaction_corr,
        countif(rain_sensitivity_segment = 'Rain-positive demand') as rain_positive_categories,
        countif(rain_sensitivity_segment = 'Rain-negative demand') as rain_negative_categories,
        countif(rain_sensitivity_segment = 'Low rain sensitivity') as low_rain_sensitivity_categories,
        countif(rain_sensitivity_segment = 'Limited comparison') as limited_comparison_categories,
        safe_divide(countif(rain_sensitivity_segment = 'Rain-positive demand'), count(*)) as rain_positive_category_share,
        safe_divide(countif(rain_sensitivity_segment = 'Rain-negative demand'), count(*)) as rain_negative_category_share
    from weather_sensitivity
    group by market_id
)

select
    market_opportunity.market_id,
    market_opportunity.market_name,
    market_opportunity.nova_region,
    market_opportunity.country_name,
    market_opportunity.country_iso3,
    market_opportunity.country_region,
    market_opportunity.country_subregion,
    market_opportunity.latitude,
    market_opportunity.longitude,

    market_opportunity.total_transactions,
    market_opportunity.total_gmv_usd,
    market_opportunity.avg_daily_transactions,
    market_opportunity.avg_daily_gmv_usd,
    market_opportunity.avg_transaction_amount_usd,
    market_opportunity.annual_active_users,
    market_opportunity.market_active_user_penetration,
    market_opportunity.market_urban_active_user_penetration,
    market_opportunity.country_active_user_penetration,
    market_opportunity.country_urban_active_user_penetration,

    market_opportunity.transaction_growth_rate,
    market_opportunity.gmv_growth_rate,
    market_opportunity.completion_rate,
    market_opportunity.failed_rate,
    market_opportunity.refunded_rate,
    market_opportunity.promo_share,
    market_opportunity.ios_transaction_share,
    market_opportunity.android_transaction_share,
    market_opportunity.lite_transaction_share,
    market_opportunity.web_transaction_share,

    market_opportunity.active_services,
    market_opportunity.avg_service_rating,
    market_opportunity.avg_popularity_score,
    market_opportunity.head_services,
    market_opportunity.mid_services,
    market_opportunity.long_tail_services,
    market_opportunity.head_service_share,
    market_opportunity.mid_service_share,
    market_opportunity.long_tail_service_share,

    market_opportunity.population_total,
    market_opportunity.gdp_per_capita_current_usd,
    market_opportunity.urban_population_pct,
    market_opportunity.internet_users_pct,
    market_opportunity.mobile_subscriptions_per_100_people,
    market_opportunity.market_weight,
    market_opportunity.growth_multiplier,
    market_opportunity.configured_ios_share,

    market_opportunity.current_performance_score,
    market_opportunity.growth_score,
    market_opportunity.macro_potential_score,
    market_opportunity.reliability_score,
    market_opportunity.supply_score,
    market_opportunity.adoption_score,
    market_opportunity.opportunity_score,
    market_opportunity.opportunity_rank,
    market_opportunity.opportunity_segment,

    coalesce(category_mix.food_delivery_transaction_share, 0) as food_delivery_transaction_share,
    coalesce(category_mix.ride_hailing_transaction_share, 0) as ride_hailing_transaction_share,
    coalesce(category_mix.e_commerce_transaction_share, 0) as e_commerce_transaction_share,
    coalesce(category_mix.grocery_transaction_share, 0) as grocery_transaction_share,
    coalesce(category_mix.digital_wallet_transaction_share, 0) as digital_wallet_transaction_share,
    coalesce(category_mix.food_delivery_gmv_share, 0) as food_delivery_gmv_share,
    coalesce(category_mix.ride_hailing_gmv_share, 0) as ride_hailing_gmv_share,
    coalesce(category_mix.e_commerce_gmv_share, 0) as e_commerce_gmv_share,
    coalesce(category_mix.grocery_gmv_share, 0) as grocery_gmv_share,
    coalesce(category_mix.digital_wallet_gmv_share, 0) as digital_wallet_gmv_share,

    daily_weather_context.avg_temperature_2m_mean_c,
    daily_weather_context.avg_precipitation_sum_mm,
    daily_weather_context.avg_rain_sum_mm,
    daily_weather_context.avg_precipitation_hours,
    daily_weather_context.avg_wind_speed_10m_max_kmh,
    daily_weather_context.rain_day_share,

    coalesce(weather_sensitivity_by_market.avg_rain_transaction_lift_pct, 0) as avg_rain_transaction_lift_pct,
    coalesce(weather_sensitivity_by_market.avg_rain_gmv_lift_pct, 0) as avg_rain_gmv_lift_pct,
    coalesce(weather_sensitivity_by_market.max_abs_rain_transaction_lift_pct, 0) as max_abs_rain_transaction_lift_pct,
    coalesce(weather_sensitivity_by_market.max_abs_rain_gmv_lift_pct, 0) as max_abs_rain_gmv_lift_pct,
    weather_sensitivity_by_market.avg_precipitation_transaction_corr,
    weather_sensitivity_by_market.avg_temperature_transaction_corr,
    coalesce(weather_sensitivity_by_market.rain_positive_categories, 0) as rain_positive_categories,
    coalesce(weather_sensitivity_by_market.rain_negative_categories, 0) as rain_negative_categories,
    coalesce(weather_sensitivity_by_market.low_rain_sensitivity_categories, 0) as low_rain_sensitivity_categories,
    coalesce(weather_sensitivity_by_market.limited_comparison_categories, 0) as limited_comparison_categories,
    coalesce(weather_sensitivity_by_market.rain_positive_category_share, 0) as rain_positive_category_share,
    coalesce(weather_sensitivity_by_market.rain_negative_category_share, 0) as rain_negative_category_share
from market_opportunity
left join category_mix
    on market_opportunity.market_id = category_mix.market_id
left join daily_weather_context
    on market_opportunity.market_id = daily_weather_context.market_id
left join weather_sensitivity_by_market
    on market_opportunity.market_id = weather_sensitivity_by_market.market_id
