with fraud_features as (
    select *
    from {{ ref('ml_transaction_fraud_features') }}
),

fraud_scores as (
    select *
    from {{ source('ml_outputs', 'ml_transaction_fraud_scores_sample') }}
),

transaction_fraud_tableau as (
    select
        fraud_features.transaction_uuid,
        fraud_features.user_id,
        fraud_features.service_id,
        fraud_features.category,
        fraud_features.rating,
        fraud_features.market_id,
        fraud_features.market_name,
        fraud_features.region,
        fraud_features.country_name,
        fraud_features.country_iso2,
        fraud_features.country_iso3,
        fraud_features.world_bank_country_code,
        fraud_features.status,
        fraud_features.timestamp,
        fraud_features.order_date,
        fraud_features.order_time,
        fraud_features.transaction_hour,
        fraud_features.transaction_day_of_week,
        fraud_features.amount_usd,
        fraud_features.acquisition_source,
        fraud_features.referral_source,
        fraud_features.gps_lat,
        fraud_features.gps_long,
        fraud_features.user_segment,
        fraud_features.lifecycle_segment,
        fraud_features.service_tier,
        fraud_features.is_promo_period,
        fraud_features.user_transaction_sequence,
        fraud_features.user_transaction_count_1h,
        fraud_features.user_transaction_count_24h,
        fraud_features.user_amount_usd_24h,
        fraud_features.user_service_transaction_count_24h,
        fraud_features.user_avg_amount_usd_prev_20,
        fraud_features.user_stddev_amount_usd_prev_20,
        fraud_features.amount_vs_user_avg_prev_20,
        fraud_features.amount_zscore_user_prev_20,
        fraud_features.service_avg_amount_usd_prev_100,
        fraud_features.amount_vs_service_avg_prev_100,
        fraud_features.user_distinct_services_24h,
        fraud_features.user_distinct_markets_24h,
        fraud_features.seconds_since_previous_user_transaction,
        fraud_features.is_late_night_transaction,
        fraud_features.is_unsuccessful_or_refunded,
        fraud_scores.fraud_anomaly_score,
        fraud_scores.is_anomaly,
        fraud_scores.is_suspicious_transaction,
        case
            when fraud_scores.is_suspicious_transaction then 'Suspicious'
            else 'Normal'
        end as fraud_review_status
    from fraud_scores
    inner join fraud_features
        on fraud_scores.transaction_uuid = fraud_features.transaction_uuid
)

select * from transaction_fraud_tableau
