with interactions as (
    select *
    from {{ ref('stg_interactions') }}
),

services as (
    select *
    from {{ ref('int_services_enriched') }}
),

transaction_features as (
    select
        interactions.transaction_id as transaction_uuid,
        interactions.user_id,
        interactions.service_id,
        interactions.category,
        services.rating,
        coalesce(interactions.market_id, services.market_id) as market_id,
        coalesce(interactions.market_name, services.market_name) as market_name,
        coalesce(interactions.region, services.region) as region,
        services.country_name,
        services.country_iso2,
        services.country_iso3,
        services.world_bank_country_code,
        interactions.status,
        interactions.timestamp,
        interactions.order_date,
        interactions.order_time,
        extract(hour from interactions.timestamp) as transaction_hour,
        extract(dayofweek from interactions.timestamp) as transaction_day_of_week,
        interactions.amount as amount_usd,
        interactions.acquisition_source,
        interactions.platform_user_agent,
        interactions.referral_source,
        interactions.gps_lat,
        interactions.gps_long,
        interactions.user_segment,
        interactions.lifecycle_segment,
        coalesce(interactions.service_tier, services.service_tier) as service_tier,
        interactions.is_promo_period,
        row_number() over (
            partition by interactions.user_id
            order by interactions.timestamp, interactions.transaction_id
        ) as user_transaction_sequence,
        count(*) over (
            partition by interactions.user_id
            order by unix_seconds(interactions.timestamp)
            range between 3600 preceding and current row
        ) as user_transaction_count_1h,
        count(*) over (
            partition by interactions.user_id
            order by unix_seconds(interactions.timestamp)
            range between 86400 preceding and current row
        ) as user_transaction_count_24h,
        sum(interactions.amount) over (
            partition by interactions.user_id
            order by unix_seconds(interactions.timestamp)
            range between 86400 preceding and current row
        ) as user_amount_usd_24h,
        count(*) over (
            partition by interactions.user_id, interactions.service_id
            order by unix_seconds(interactions.timestamp)
            range between 86400 preceding and current row
        ) as user_service_transaction_count_24h,
        avg(interactions.amount) over (
            partition by interactions.user_id
            order by interactions.timestamp, interactions.transaction_id
            rows between 20 preceding and 1 preceding
        ) as user_avg_amount_usd_prev_20,
        stddev_samp(interactions.amount) over (
            partition by interactions.user_id
            order by interactions.timestamp, interactions.transaction_id
            rows between 20 preceding and 1 preceding
        ) as user_stddev_amount_usd_prev_20,
        safe_divide(
            interactions.amount,
            avg(interactions.amount) over (
                partition by interactions.user_id
                order by interactions.timestamp, interactions.transaction_id
                rows between 20 preceding and 1 preceding
            )
        ) as amount_vs_user_avg_prev_20,
        safe_divide(
            interactions.amount - avg(interactions.amount) over (
                partition by interactions.user_id
                order by interactions.timestamp, interactions.transaction_id
                rows between 20 preceding and 1 preceding
            ),
            stddev_samp(interactions.amount) over (
                partition by interactions.user_id
                order by interactions.timestamp, interactions.transaction_id
                rows between 20 preceding and 1 preceding
            )
        ) as amount_zscore_user_prev_20,
        avg(interactions.amount) over (
            partition by interactions.service_id
            order by interactions.timestamp, interactions.transaction_id
            rows between 100 preceding and 1 preceding
        ) as service_avg_amount_usd_prev_100,
        safe_divide(
            interactions.amount,
            avg(interactions.amount) over (
                partition by interactions.service_id
                order by interactions.timestamp, interactions.transaction_id
                rows between 100 preceding and 1 preceding
            )
        ) as amount_vs_service_avg_prev_100,
        (
            select count(distinct prior_interactions.service_id)
            from interactions as prior_interactions
            where prior_interactions.user_id = interactions.user_id
                and prior_interactions.timestamp between timestamp_sub(interactions.timestamp, interval 24 hour)
                and interactions.timestamp
        ) as user_distinct_services_24h,
        (
            select count(distinct prior_interactions.market_id)
            from interactions as prior_interactions
            where prior_interactions.user_id = interactions.user_id
                and prior_interactions.timestamp between timestamp_sub(interactions.timestamp, interval 24 hour)
                and interactions.timestamp
        ) as user_distinct_markets_24h,
        lag(interactions.timestamp) over (
            partition by interactions.user_id
            order by interactions.timestamp, interactions.transaction_id
        ) as previous_user_transaction_at,
        timestamp_diff(
            interactions.timestamp,
            lag(interactions.timestamp) over (
                partition by interactions.user_id
                order by interactions.timestamp, interactions.transaction_id
            ),
            second
        ) as seconds_since_previous_user_transaction,
        lag(interactions.gps_lat) over (
            partition by interactions.user_id
            order by interactions.timestamp, interactions.transaction_id
        ) as previous_user_gps_lat,
        lag(interactions.gps_long) over (
            partition by interactions.user_id
            order by interactions.timestamp, interactions.transaction_id
        ) as previous_user_gps_long,
        case
            when extract(hour from interactions.timestamp) between 0 and 5 then true
            else false
        end as is_late_night_transaction,
        case
            when lower(interactions.status) in ('failed', 'refunded') then true
            else false
        end as is_unsuccessful_or_refunded
    from interactions
    left join services
        on interactions.service_id = services.service_id
)

select * from transaction_features
