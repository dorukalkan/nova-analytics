{{ config(schema=target.schema) }}

with source as (
    select *
    from {{ ref('market_country_lookup') }}
),

cleaned as (
    select
        cast(market_id as int64) as market_id,
        market_name,
        country_name,
        country_iso2,
        country_iso3,
        world_bank_country_code,
        source as seed_source,
        fetched_at_utc as seed_fetched_at
    from source
)

select * from cleaned
