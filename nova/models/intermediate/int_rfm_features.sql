with customer_metrics as (

    select *
    from {{ ref('int_customer_metrics') }}

),

max_order_date as (

    select
        max(last_order_date) as reference_date
    from customer_metrics

),

rfm_features as (

    select
        cm.user_id,

        date_diff(mod.reference_date, cm.last_order_date, day) as recency,

        cm.transaction_count as frequency,

        cm.total_spend as monetary

    from customer_metrics cm
    cross join max_order_date mod

)

select *
from rfm_features