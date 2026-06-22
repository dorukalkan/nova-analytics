with interactions as (
    select *
    from {{ ref('stg_interactions') }}
),

aggregated as (
    select
        market_id,
        market_name,
        region,
        category,
        extract(hour from timestamp) as hour_of_day,
        count(*) as transactions,
        sum(amount) as gmv_usd,
        avg(amount) as avg_transaction_amount_usd,
        count(distinct user_id) as active_users,
        countif(status = 'Completed') as completed_transactions,
        countif(status = 'Failed') as failed_transactions,
        countif(status = 'Refunded') as refunded_transactions,
        safe_divide(countif(status = 'Completed'), count(*)) as completion_rate
    from interactions
    group by 1, 2, 3, 4, 5
)

select * from aggregated
