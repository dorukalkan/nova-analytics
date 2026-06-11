{{ config(schema=target.schema) }}

with raw_seed as (
    select *
    from {{ ref('ext_country_metadata') }}
),

cleaned as (
    select
        country_iso3,
        country_iso2,
        country_name_common,
        country_name_official,
        region,
        subregion,
        capital,
        currency_code,
        currency_name,
        currency_symbol,
        population,
        timezones,
        raw_seed.source as seed_source,
        fetched_at_utc as seed_fetched_at
    from raw_seed
)

select * from cleaned
