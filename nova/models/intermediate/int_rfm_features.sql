with customer_metrics as (

    select *
    from {{ ref('int_customer_metrics') }}

),

rfm_features as (

    select
        user_id,

        date_diff(current_date(), last_order_date, day) as recency,

        transaction_count as frequency,

        total_spend as monetary

    from customer_metrics

)

select *
from rfm_features