{{ config(schema=target.schema) }}

with raw_seed as (
    select *
    from {{ ref('ext_world_bank_indicators') }}
),

cleaned as (
    select
        country_iso3,
        country_name,
        indicator_code,
        metric_name,
        indicator_name,
        cast(indicator_year as int64) as indicator_year,
        indicator_value,
        raw_seed.source as seed_source,
        fetched_at_utc as seed_fetched_at
    from raw_seed
)

select * from cleaned
