with category_day as (
    select
        market_id,
        order_date,
        sum(transactions) as category_transactions,
        sum(gmv_usd) as category_gmv_usd
    from {{ ref('mart_geo_market_category_day_features') }}
    group by 1, 2
),

market_day as (
    select
        market_id,
        order_date,
        transactions as market_transactions,
        gmv_usd as market_gmv_usd
    from {{ ref('int_geo_market_day_metrics') }}
)

select
    category_day.market_id,
    category_day.order_date,
    category_day.category_transactions,
    market_day.market_transactions,
    category_day.category_transactions - market_day.market_transactions as transaction_diff,
    category_day.category_gmv_usd,
    market_day.market_gmv_usd,
    category_day.category_gmv_usd - market_day.market_gmv_usd as gmv_diff
from category_day
inner join market_day
    on category_day.market_id = market_day.market_id
    and category_day.order_date = market_day.order_date
where abs(category_day.category_transactions - market_day.market_transactions) > 0
    or abs(category_day.category_gmv_usd - market_day.market_gmv_usd) > 0.01
