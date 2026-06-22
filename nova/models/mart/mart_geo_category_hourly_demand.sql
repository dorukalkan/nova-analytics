with markets as (
    select *
    from {{ ref('stg_markets') }}
),

categories as (
    select distinct category
    from {{ ref('stg_interactions') }}
),

hours as (
    select hour_of_day
    from unnest(generate_array(0, 23)) as hour_of_day
),

spine as (
    select
        markets.market_id,
        markets.market_name,
        markets.region as nova_region,
        categories.category,
        hours.hour_of_day
    from markets
    cross join categories
    cross join hours
),

metrics as (
    select *
    from {{ ref('int_geo_market_category_hour_metrics') }}
),

with_metrics as (
    select
        concat(
            cast(spine.market_id as string),
            '|',
            spine.category,
            '|',
            lpad(cast(spine.hour_of_day as string), 2, '0')
        ) as market_category_hour_id,
        spine.market_id,
        spine.market_name,
        spine.nova_region,
        spine.category,
        spine.hour_of_day,
        format('%02d:00', spine.hour_of_day) as hour_label,
        coalesce(metrics.transactions, 0) as transactions,
        coalesce(metrics.gmv_usd, 0) as gmv_usd,
        coalesce(metrics.avg_transaction_amount_usd, 0) as avg_transaction_amount_usd,
        coalesce(metrics.active_users, 0) as active_users,
        coalesce(metrics.completed_transactions, 0) as completed_transactions,
        coalesce(metrics.failed_transactions, 0) as failed_transactions,
        coalesce(metrics.refunded_transactions, 0) as refunded_transactions,
        coalesce(metrics.completion_rate, 0) as completion_rate
    from spine
    left join metrics
        on spine.market_id = metrics.market_id
        and spine.category = metrics.category
        and spine.hour_of_day = metrics.hour_of_day
),

with_shares as (
    select
        *,
        safe_divide(
            transactions,
            nullif(sum(transactions) over (partition by market_id, category), 0)
        ) as transaction_share_within_market_category,
        safe_divide(
            gmv_usd,
            nullif(sum(gmv_usd) over (partition by market_id, category), 0)
        ) as gmv_share_within_market_category
    from with_metrics
)

select * from with_shares
