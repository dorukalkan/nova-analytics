with services as (
    select *
    from {{ ref('stg_services') }}
),

market_country_lookup as (
    select *
    from {{ ref('stg_geo_market_country_lookup') }}
),

services_enriched as (
    select
        services.service_id,
        services.merchant_name,
        services.category,
        services.rating,
        services.market_id,
        services.market_name,
        services.region,
        services.service_tier,
        services.popularity_score,
        market_country_lookup.country_name,
        market_country_lookup.country_iso2,
        market_country_lookup.country_iso3,
        market_country_lookup.world_bank_country_code
    from services
    left join market_country_lookup
        on services.market_id = market_country_lookup.market_id
)

select * from services_enriched
