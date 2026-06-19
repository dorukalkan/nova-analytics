with markets as (
    select *
    from {{ ref('stg_markets') }}
),

market_country as (
    select *
    from {{ ref('stg_geo_market_country_lookup') }}
),

country_metadata as (
    select *
    from {{ ref('stg_geo_country_metadata') }}
),

macro as (
    select *
    from {{ ref('int_geo_country_macro_pivot') }}
),

joined as (
    select
        markets.market_id,
        markets.market_name,
        markets.region as nova_region,
        markets.latitude,
        markets.longitude,
        markets.market_weight,
        markets.growth_multiplier,
        markets.ios_share,
        market_country.country_name,
        market_country.country_iso2,
        market_country.country_iso3,
        market_country.world_bank_country_code,
        country_metadata.country_name_common,
        country_metadata.country_name_official,
        country_metadata.region as country_region,
        country_metadata.subregion as country_subregion,
        country_metadata.capital as country_capital,
        country_metadata.currency_code,
        country_metadata.currency_name,
        country_metadata.currency_symbol,
        country_metadata.population as country_metadata_population,
        country_metadata.timezones,
        macro.population_total,
        macro.gdp_per_capita_current_usd,
        macro.urban_population_pct,
        macro.internet_users_pct,
        macro.mobile_subscriptions_per_100_people,
        macro.population_total_year,
        macro.gdp_per_capita_year,
        macro.urban_population_year,
        macro.internet_users_year,
        macro.mobile_subscriptions_year
    from markets
    left join market_country
        on markets.market_id = market_country.market_id
    left join country_metadata
        on market_country.country_iso3 = country_metadata.country_iso3
    left join macro
        on market_country.country_iso3 = macro.country_iso3
)

select * from joined
