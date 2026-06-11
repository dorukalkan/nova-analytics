{{ config(schema=target.schema) }}

with source as (
    select *
    from {{ ref('ext_weather_daily') }}
),

cleaned as (
    select
        cast(market_id as int64) as market_id,
        market_name,
        weather_date,
        cast(weather_code as int64) as weather_code,
        temperature_2m_mean_c,
        temperature_2m_max_c,
        temperature_2m_min_c,
        apparent_temperature_mean_c,
        precipitation_sum_mm,
        rain_sum_mm,
        precipitation_hours,
        wind_speed_10m_max_kmh,
        is_rain_day,
        source as seed_source,
        fetched_at_utc as seed_fetched_at
    from source
)

select * from cleaned
