with rfm_scores as (

    select *
    from {{ ref('int_rfm_scores') }}

),

customer_segments as (

    select
        *,

        case

            when recency_score >= 5
             and frequency_score >= 4
             and monetary_score >= 4
                then 'Champions'

            when recency_score >= 3
             and frequency_score >= 4
                then 'Loyal Customers'

            when recency_score >= 4
             and frequency_score <= 2
                then 'New Customers'

            when monetary_score = 5
             and frequency_score <= 3
                then 'Big Spenders'

            when recency_score <= 2
             and frequency_score >= 3
                then 'At Risk'

            when recency_score = 1
                then 'Lost Customers'

            else 'Potential Loyalists'

        end as customer_segment

    from rfm_scores

)

select *
from customer_segments