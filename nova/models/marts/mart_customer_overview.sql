{{ config(materialized='table') }}

with users as (

    select
        user_id,
        membership_tier,
        primary_device,
        market_id,
        market_name,
        region,
        acquisition_source,
        user_segment,
        lifecycle_segment,
        join_date
    from {{ ref('stg_users') }}

),

interactions as (

    select
        user_id,
        transaction_id,
        amount,
        status,
        order_date
    from {{ ref('stg_interactions') }}

),

customer_metrics as (

    select
        user_id,

        count(distinct transaction_id) as transaction_count,

        count(distinct case 
            when status = 'Completed' then transaction_id 
        end) as completed_transaction_count,

        sum(case 
            when status = 'Completed' then amount 
            else 0 
        end) as total_revenue,

        avg(case 
            when status = 'Completed' then amount 
        end) as avg_order_value,

        min(order_date) as first_order_date,
        max(order_date) as last_order_date

    from interactions
    group by user_id

),

final as (

    select
        u.user_id,
        u.membership_tier,
        u.primary_device,
        u.market_id,
        u.market_name,
        u.region,
        u.acquisition_source,
        u.user_segment,
        u.lifecycle_segment,
        u.join_date,

        coalesce(cm.transaction_count, 0) as transaction_count,
        coalesce(cm.completed_transaction_count, 0) as completed_transaction_count,
        coalesce(cm.total_revenue, 0) as total_revenue,
        coalesce(cm.avg_order_value, 0) as avg_order_value,

        cm.first_order_date,
        cm.last_order_date,

        date_diff(current_date(), u.join_date, day) as customer_age_days,
        date_diff(current_date(), cm.last_order_date, day) as days_since_last_order

    from users u
    left join customer_metrics cm
        on u.user_id = cm.user_id

)

select *
from final