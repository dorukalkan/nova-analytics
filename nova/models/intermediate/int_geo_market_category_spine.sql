with markets as (
    select
        market_id,
        market_name,
        region
    from {{ ref('stg_markets') }}
),

categories as (
    select distinct category
    from {{ ref('stg_services') }}
),

dates as (
    select order_date
    from {{ ref('int_geo_date_spine') }}
),

spine as (
    select
        markets.market_id,
        markets.market_name,
        markets.region,
        categories.category,
        dates.order_date
    from markets
    cross join categories
    cross join dates
)

select * from spine
