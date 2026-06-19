with services as (
    select *
    from {{ ref('stg_services') }}
),

aggregated as (
    select
        market_id,
        market_name,
        region,
        category,
        count(distinct service_id) as active_services,
        avg(rating) as avg_service_rating,
        avg(popularity_score) as avg_popularity_score,
        countif(service_tier = 'Head') as head_services,
        countif(service_tier = 'Mid') as mid_services,
        countif(service_tier = 'Long Tail') as long_tail_services,
        safe_divide(countif(service_tier = 'Head'), count(distinct service_id)) as head_service_share,
        safe_divide(countif(service_tier = 'Mid'), count(distinct service_id)) as mid_service_share,
        safe_divide(countif(service_tier = 'Long Tail'), count(distinct service_id)) as long_tail_service_share
    from services
    group by 1, 2, 3, 4
)

select * from aggregated
