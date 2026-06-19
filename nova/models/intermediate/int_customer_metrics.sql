with interactions as (

    select *
    from {{ ref('stg_interactions') }}

),

customer_metrics as (

    select
        user_id,

        count(distinct transaction_id) as transaction_count,
        sum(amount) as total_spend,
        avg(amount) as avg_order_value,

        min(order_date) as first_order_date,
        max(order_date) as last_order_date,

        date_diff(max(order_date), min(order_date), day) as customer_lifetime_days,

        count(distinct category) as category_count,
        count(distinct service_id) as unique_services_used

    from interactions
    group by user_id

)

select *
from customer_metrics