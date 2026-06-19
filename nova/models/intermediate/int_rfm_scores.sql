with rfm_features as (

    select *
    from {{ ref('int_rfm_features') }}

)

select
    user_id,
    recency,
    frequency,
    monetary,

    ntile(5) over(order by recency desc) as recency_score,

    ntile(5) over(order by frequency) as frequency_score,

    ntile(5) over(order by monetary) as monetary_score

from rfm_features