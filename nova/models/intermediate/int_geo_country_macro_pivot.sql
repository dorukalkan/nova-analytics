with indicators as (
    select *
    from {{ ref('stg_geo_world_bank_indicators') }}
),

pivoted as (
    select
        country_iso3,
        any_value(country_name) as country_name,
        max(if(metric_name = 'population_total', indicator_value, null)) as population_total,
        max(if(metric_name = 'gdp_per_capita_current_usd', indicator_value, null)) as gdp_per_capita_current_usd,
        max(if(metric_name = 'urban_population_pct', indicator_value, null)) as urban_population_pct,
        max(if(metric_name = 'internet_users_pct', indicator_value, null)) as internet_users_pct,
        max(if(metric_name = 'mobile_subscriptions_per_100_people', indicator_value, null)) as mobile_subscriptions_per_100_people,
        max(if(metric_name = 'population_total', indicator_year, null)) as population_total_year,
        max(if(metric_name = 'gdp_per_capita_current_usd', indicator_year, null)) as gdp_per_capita_year,
        max(if(metric_name = 'urban_population_pct', indicator_year, null)) as urban_population_year,
        max(if(metric_name = 'internet_users_pct', indicator_year, null)) as internet_users_year,
        max(if(metric_name = 'mobile_subscriptions_per_100_people', indicator_year, null)) as mobile_subscriptions_year
    from indicators
    group by country_iso3
)

select * from pivoted
