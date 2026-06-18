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
        order_date,
        count(*) as transactions,
        sum(amount) as gmv_usd,
        avg(amount) as avg_transaction_amount_usd,
        count(distinct user_id) as active_users,
        count(distinct service_id) as active_services_with_transactions,
        countif(status = 'Completed') as completed_transactions,
        countif(status = 'Failed') as failed_transactions,
        countif(status = 'Refunded') as refunded_transactions,
        countif(is_promo_period) as promo_transactions,
        countif(service_tier = 'Head') as head_tier_transactions,
        countif(service_tier = 'Mid') as mid_tier_transactions,
        countif(service_tier = 'Long Tail') as long_tail_tier_transactions,
        countif(platform_user_agent like '%iOS%') as ios_transactions,
        countif(platform_user_agent like '%Android 14%') as android_transactions,
        countif(platform_user_agent like '%Lite%') as lite_transactions,
        countif(platform_user_agent like '%Web Portal%') as web_transactions,
        safe_divide(countif(status = 'Completed'), count(*)) as completion_rate,
        safe_divide(countif(status = 'Failed'), count(*)) as failed_rate,
        safe_divide(countif(status = 'Refunded'), count(*)) as refunded_rate,
        safe_divide(countif(is_promo_period), count(*)) as promo_share,
        safe_divide(countif(service_tier = 'Head'), count(*)) as head_tier_transaction_share,
        safe_divide(countif(service_tier = 'Mid'), count(*)) as mid_tier_transaction_share,
        safe_divide(countif(service_tier = 'Long Tail'), count(*)) as long_tail_tier_transaction_share,
        safe_divide(countif(platform_user_agent like '%iOS%'), count(*)) as ios_transaction_share,
        safe_divide(countif(platform_user_agent like '%Android 14%'), count(*)) as android_transaction_share,
        safe_divide(countif(platform_user_agent like '%Lite%'), count(*)) as lite_transaction_share,
        safe_divide(countif(platform_user_agent like '%Web Portal%'), count(*)) as web_transaction_share
    from interactions
    group by 1, 2, 3, 4, 5
)

select * from aggregated
