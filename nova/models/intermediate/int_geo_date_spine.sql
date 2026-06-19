with bounds as (
    select
        min(weather_date) as start_date,
        max(weather_date) as end_date
    from {{ ref('stg_geo_weather_daily') }}
),

dates as (
    select date_day
    from bounds,
    unnest(generate_date_array(start_date, end_date)) as date_day
),

enriched as (
    select
        date_day as order_date,
        extract(year from date_day) as year,
        extract(quarter from date_day) as quarter,
        extract(month from date_day) as month,
        format_date('%Y-%m', date_day) as year_month,
        extract(dayofweek from date_day) as day_of_week,
        format_date('%A', date_day) as day_name,
        extract(dayofweek from date_day) in (1, 7) as is_weekend
    from dates
)

select * from enriched
