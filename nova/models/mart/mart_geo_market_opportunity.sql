with market_context as (
    select *
    from {{ ref('int_geo_market_context') }}
),

market_day_metrics as (
    select *
    from {{ ref('int_geo_market_day_metrics') }}
),

service_supply as (
    select *
    from {{ ref('int_geo_service_supply_by_market_category') }}
),

annual_market_users as (
    select
        market_id,
        count(distinct user_id) as annual_active_users
    from {{ ref('stg_interactions') }}
    group by market_id
),

annual_market_metrics as (
    select
        market_id,
        any_value(market_name) as market_name,
        any_value(region) as nova_region,
        count(*) as observed_days,
        sum(transactions) as total_transactions,
        sum(gmv_usd) as total_gmv_usd,
        sum(active_users) as active_user_days,
        avg(transactions) as avg_daily_transactions,
        avg(gmv_usd) as avg_daily_gmv_usd,
        safe_divide(sum(gmv_usd), nullif(sum(transactions), 0)) as avg_transaction_amount_usd,
        safe_divide(sum(completed_transactions), nullif(sum(transactions), 0)) as completion_rate,
        safe_divide(sum(failed_transactions), nullif(sum(transactions), 0)) as failed_rate,
        safe_divide(sum(refunded_transactions), nullif(sum(transactions), 0)) as refunded_rate,
        safe_divide(sum(promo_transactions), nullif(sum(transactions), 0)) as promo_share,
        safe_divide(sum(ios_transactions), nullif(sum(transactions), 0)) as ios_transaction_share,
        safe_divide(sum(android_transactions), nullif(sum(transactions), 0)) as android_transaction_share,
        safe_divide(sum(lite_transactions), nullif(sum(transactions), 0)) as lite_transaction_share,
        safe_divide(sum(web_transactions), nullif(sum(transactions), 0)) as web_transaction_share
    from market_day_metrics
    group by market_id
),

monthly_market_metrics as (
    select
        market_id,
        date_trunc(order_date, month) as month_start,
        count(*) as observed_days,
        sum(transactions) as monthly_transactions,
        sum(gmv_usd) as monthly_gmv_usd,
        safe_divide(sum(transactions), count(*)) as avg_daily_transactions,
        safe_divide(sum(gmv_usd), count(*)) as avg_daily_gmv_usd
    from market_day_metrics
    group by 1, 2
),

market_growth as (
    select
        market_id,
        max(if(month_start = date '2024-01-01', avg_daily_transactions, null)) as jan_avg_daily_transactions,
        max(if(month_start = date '2024-12-01', avg_daily_transactions, null)) as dec_avg_daily_transactions,
        max(if(month_start = date '2024-01-01', avg_daily_gmv_usd, null)) as jan_avg_daily_gmv_usd,
        max(if(month_start = date '2024-12-01', avg_daily_gmv_usd, null)) as dec_avg_daily_gmv_usd
    from monthly_market_metrics
    group by market_id
),

service_supply_by_market as (
    select
        market_id,
        sum(active_services) as active_services,
        safe_divide(sum(avg_service_rating * active_services), nullif(sum(active_services), 0)) as avg_service_rating,
        safe_divide(sum(avg_popularity_score * active_services), nullif(sum(active_services), 0)) as avg_popularity_score,
        sum(head_services) as head_services,
        sum(mid_services) as mid_services,
        sum(long_tail_services) as long_tail_services,
        safe_divide(sum(head_services), nullif(sum(active_services), 0)) as head_service_share,
        safe_divide(sum(mid_services), nullif(sum(active_services), 0)) as mid_service_share,
        safe_divide(sum(long_tail_services), nullif(sum(active_services), 0)) as long_tail_service_share
    from service_supply
    group by market_id
),

joined as (
    select
        market_context.market_id,
        market_context.market_name,
        market_context.nova_region,
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
        annual_market_metrics.observed_days,
        annual_market_metrics.total_transactions,
        annual_market_metrics.total_gmv_usd,
        annual_market_metrics.active_user_days,
        annual_market_metrics.avg_daily_transactions,
        annual_market_metrics.avg_daily_gmv_usd,
        annual_market_metrics.avg_transaction_amount_usd,
        annual_market_metrics.completion_rate,
        annual_market_metrics.failed_rate,
        annual_market_metrics.refunded_rate,
        annual_market_metrics.promo_share,
        annual_market_metrics.ios_transaction_share,
        annual_market_metrics.android_transaction_share,
        annual_market_metrics.lite_transaction_share,
        annual_market_metrics.web_transaction_share,
        market_growth.jan_avg_daily_transactions,
        market_growth.dec_avg_daily_transactions,
        safe_divide(
            market_growth.dec_avg_daily_transactions - market_growth.jan_avg_daily_transactions,
            nullif(market_growth.jan_avg_daily_transactions, 0)
        ) as transaction_growth_rate,
        market_growth.jan_avg_daily_gmv_usd,
        market_growth.dec_avg_daily_gmv_usd,
        safe_divide(
            market_growth.dec_avg_daily_gmv_usd - market_growth.jan_avg_daily_gmv_usd,
            nullif(market_growth.jan_avg_daily_gmv_usd, 0)
        ) as gmv_growth_rate,
        service_supply_by_market.active_services,
        service_supply_by_market.avg_service_rating,
        service_supply_by_market.avg_popularity_score,
        service_supply_by_market.head_services,
        service_supply_by_market.mid_services,
        service_supply_by_market.long_tail_services,
        service_supply_by_market.head_service_share,
        service_supply_by_market.mid_service_share,
        service_supply_by_market.long_tail_service_share
    from market_context
    left join annual_market_metrics
        on market_context.market_id = annual_market_metrics.market_id
    left join market_growth
        on market_context.market_id = market_growth.market_id
    left join service_supply_by_market
        on market_context.market_id = service_supply_by_market.market_id
),

with_adoption as (
    select
        joined.*,
        annual_market_users.annual_active_users,
        sum(annual_market_users.annual_active_users) over (
            partition by joined.country_iso3
        ) as country_annual_active_users,
        safe_divide(
            annual_market_users.annual_active_users,
            nullif(joined.population_total, 0)
        ) as market_active_user_penetration,
        safe_divide(
            annual_market_users.annual_active_users,
            nullif(joined.population_total * joined.urban_population_pct / 100, 0)
        ) as market_urban_active_user_penetration,
        safe_divide(
            sum(annual_market_users.annual_active_users) over (
                partition by joined.country_iso3
            ),
            nullif(joined.population_total, 0)
        ) as country_active_user_penetration,
        safe_divide(
            sum(annual_market_users.annual_active_users) over (
                partition by joined.country_iso3
            ),
            nullif(joined.population_total * joined.urban_population_pct / 100, 0)
        ) as country_urban_active_user_penetration
    from joined
    left join annual_market_users
        on joined.market_id = annual_market_users.market_id
),

normalized as (
    select
        with_adoption.*,
        safe_divide(total_transactions - min(total_transactions) over (), nullif(max(total_transactions) over () - min(total_transactions) over (), 0)) as transactions_norm,
        safe_divide(total_gmv_usd - min(total_gmv_usd) over (), nullif(max(total_gmv_usd) over () - min(total_gmv_usd) over (), 0)) as gmv_norm,
        safe_divide(active_user_days - min(active_user_days) over (), nullif(max(active_user_days) over () - min(active_user_days) over (), 0)) as active_user_days_norm,
        safe_divide(population_total - min(population_total) over (), nullif(max(population_total) over () - min(population_total) over (), 0)) as population_norm,
        safe_divide(gdp_per_capita_current_usd - min(gdp_per_capita_current_usd) over (), nullif(max(gdp_per_capita_current_usd) over () - min(gdp_per_capita_current_usd) over (), 0)) as gdp_per_capita_norm,
        safe_divide(urban_population_pct - min(urban_population_pct) over (), nullif(max(urban_population_pct) over () - min(urban_population_pct) over (), 0)) as urban_population_norm,
        safe_divide(internet_users_pct - min(internet_users_pct) over (), nullif(max(internet_users_pct) over () - min(internet_users_pct) over (), 0)) as internet_users_norm,
        safe_divide(mobile_subscriptions_per_100_people - min(mobile_subscriptions_per_100_people) over (), nullif(max(mobile_subscriptions_per_100_people) over () - min(mobile_subscriptions_per_100_people) over (), 0)) as mobile_subscriptions_norm,
        safe_divide(active_services - min(active_services) over (), nullif(max(active_services) over () - min(active_services) over (), 0)) as active_services_norm,
        safe_divide(avg_service_rating - min(avg_service_rating) over (), nullif(max(avg_service_rating) over () - min(avg_service_rating) over (), 0)) as avg_service_rating_norm,
        safe_divide(country_active_user_penetration - min(country_active_user_penetration) over (), nullif(max(country_active_user_penetration) over () - min(country_active_user_penetration) over (), 0)) as country_active_user_penetration_norm,
        safe_divide(country_urban_active_user_penetration - min(country_urban_active_user_penetration) over (), nullif(max(country_urban_active_user_penetration) over () - min(country_urban_active_user_penetration) over (), 0)) as country_urban_active_user_penetration_norm
    from with_adoption
),

scored as (
    select
        normalized.*,
        100 * (
            coalesce(transactions_norm, 0)
            + coalesce(gmv_norm, 0)
            + coalesce(active_user_days_norm, 0)
        ) / 3 as current_performance_score,
        100 * least(greatest(coalesce(transaction_growth_rate, 0), 0), 1) as growth_score,
        100 * (
            coalesce(population_norm, 0)
            + coalesce(gdp_per_capita_norm, 0)
            + coalesce(urban_population_norm, 0)
            + coalesce(internet_users_norm, 0)
            + coalesce(mobile_subscriptions_norm, 0)
        ) / 5 as macro_potential_score,
        100 * coalesce(completion_rate, 0) as reliability_score,
        100 * (
            coalesce(active_services_norm, 0)
            + coalesce(avg_service_rating_norm, 0)
        ) / 2 as supply_score,
        100 * (
            coalesce(country_active_user_penetration_norm, 0)
            + coalesce(country_urban_active_user_penetration_norm, 0)
        ) / 2 as adoption_score
    from normalized
),

final as (
    select
        *,
        round(
            0.35 * current_performance_score
            + 0.25 * macro_potential_score
            + 0.20 * supply_score
            + 0.20 * adoption_score,
            2
        ) as opportunity_score
    from scored
)

select
    *,
    rank() over (order by opportunity_score desc) as opportunity_rank,
    case
        when opportunity_score >= 75 then 'Scale priority'
        when opportunity_score >= 60 then 'Growth candidate'
        when opportunity_score >= 45 then 'Maintain'
        else 'Monitor'
    end as opportunity_segment
from final
