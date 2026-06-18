# Corrected Nova Dataset Validation

Generated validation status: **PASS**

Input directory: `data/corrected`

Expected rows: `50,000,000`

Actual rows: `50,000,000`

## BigQuery readiness checks

| check | status | detail |
| --- | --- | --- |
| Exact target row count | PASS | 50,000,000 / 50,000,000 |
| Non-partitioned interactions file exists | PASS | data/corrected/nova_interactions.parquet |
| Non-partitioned row count matches partitions | PASS | 50,000,000 / 50,000,000 |
| Non-partitioned schema matches partitions | PASS | match |
| Non-partitioned monthly totals match partitions | PASS | max row diff 0; max amount diff $0.00 |
| Unique Transaction_UUID | PASS | 50,000,000 unique |
| All required columns present | PASS | all present |
| Zero nulls in required columns | PASS | 0 nulls |
| Full date coverage | PASS | 0 missing dates |
| Category matches service category | PASS | 0 mismatches |
| User FK coverage | PASS | 0 missing |
| Service FK coverage | PASS | 0 missing |
| Annual active user rate | PASS | 85.32% |
| Lifetime repeat user rate | PASS | 84.00% |
| Category amount spread | PASS | $73.30 |
| Completion rate spread | PASS | 13.65 pp |
| Hourly CV | PASS | 50.27% |
| December/January volume ratio | PASS | 1.71x |
| Top 1pct service share | PASS | 20.32% |
| Market GPS jitter bounds | PASS | 0.808 degrees |
| Customer activity spread across lifecycle/membership | PASS | 29.89% |
| Customer non-completion spread | PASS | 2.69% |
| Market category share variation | PASS | mean std 2.41%; min std 1.58% |
| Market/category amount variation | PASS | $15.84 |
| Market/category completion variation | PASS | 0.70% |
| Market monthly growth curves not parallel | PASS | median 0.9899; max 1.0000 |
| Ride Hailing bad-weather demand lift | PASS | 6.58% |
| Food Delivery bad-weather demand lift | PASS | 7.00% |
| Digital Wallet less weather-sensitive than Ride Hailing | PASS | digital -0.84%; ride 6.58% |
| Grocery bad-weather GMV lift | PASS | 10.25% |
| Grocery bad-weather basket lift | PASS | 7.90% |
| Ride Hailing bad-weather completion penalty | PASS | -1.67% |
| Food Delivery bad-weather completion penalty | PASS | -1.19% |
| Detectable high-velocity user-hour bursts | PASS | 0.90% |
| High-velocity burst share remains moderate | PASS | 0.90% |
| High-velocity user-hours have elevated non-completion | PASS | burst 73.96%; normal 8.54% |
| High-amount transactions have elevated non-completion | PASS | high amount 13.28%; overall 9.13% |
| Suspicious proxy share is detectable | PASS | 1.10% |
| Suspicious proxy share remains moderate | PASS | 1.10% |
| New/at-risk high-amount transactions have elevated non-completion | PASS | new/at-risk 24.18%; other 13.04% |
| Suspicious proxy skews to web/lite platforms | PASS | proxy 63.37%; baseline 32.21% |
| Suspicious proxy skews to promo referrals | PASS | proxy 95.54%; baseline 56.74% |
| Digital Wallet proxy signal exceeds other categories | PASS | digital 2.12%; other 0.67% |
| E-Commerce proxy signal exceeds other categories | PASS | e-commerce 1.86%; other 0.67% |

## Monthly KPIs

| Month | n_transactions | active_users | total_amount_usd | completion_rate |
| --- | --- | --- | --- | --- |
| 2024-01-01 00:00:00 | 3300000 | 970287 | 171702812.71 | 0.9095139393939394 |
| 2024-02-01 00:00:00 | 3200000 | 962468 | 166475894.25 | 0.90933625 |
| 2024-03-01 00:00:00 | 3500000 | 1003008 | 182293007.71 | 0.9093442857142857 |
| 2024-04-01 00:00:00 | 3700000 | 1031618 | 192717080.99 | 0.9095005405405405 |
| 2024-05-01 00:00:00 | 3900000 | 1059192 | 202658277.73 | 0.9094351282051282 |
| 2024-06-01 00:00:00 | 4050000 | 1082126 | 207094114.92 | 0.9088296296296297 |
| 2024-07-01 00:00:00 | 4200000 | 1103454 | 214409840.21 | 0.9083983333333333 |
| 2024-08-01 00:00:00 | 4300000 | 1121582 | 219509228.82 | 0.9092781395348837 |
| 2024-09-01 00:00:00 | 4400000 | 1139776 | 227791440.19 | 0.9087720454545455 |
| 2024-10-01 00:00:00 | 4600000 | 1167041 | 238093395.68 | 0.9090804347826087 |
| 2024-11-01 00:00:00 | 5200000 | 1228856 | 305048510.68 | 0.9064028846153847 |
| 2024-12-01 00:00:00 | 5650000 | 1264423 | 327490704.14 | 0.9077033628318584 |

## Category KPIs

| Category | n_transactions | active_users | avg_amount_usd | median_amount_usd | completion_rate |
| --- | --- | --- | --- | --- | --- |
| Food Delivery | 14864102 | 1563353 | 28.873125557130862 | 25.39 | 0.9364854331597025 |
| Ride Hailing | 11202731 | 1485081 | 27.872597203306945 | 23.51 | 0.8800425539093994 |
| E-Commerce | 11005827 | 1482146 | 101.17087215163384 | 70.44 | 0.8652690070450862 |
| Grocery | 6915310 | 1318681 | 75.3134378762485 | 67.25 | 0.9147802484631925 |
| Digital Wallet | 6012030 | 1254551 | 46.502949840569656 | 24.26 | 0.9657563252345713 |

## Status by category and platform

| Category | Platform_User_Agent | n_transactions | completion_rate | failed_rate | refunded_rate |
| --- | --- | --- | --- | --- | --- |
| Digital Wallet | Nova App v4.2 (Android 14; Samsung S23) | 2114208 | 0.9743298672599858 | 0.022317577078508833 | 0.0033525556615053957 |
| Digital Wallet | Nova App v4.2 (iOS 17.1; iPhone 14 Pro) | 1905011 | 0.9760400333646367 | 0.02075473579942583 | 0.0032052308359374303 |
| Digital Wallet | Nova Lite (Android Go) | 910571 | 0.9575079812557176 | 0.035067007405243523 | 0.007425011339038911 |
| Digital Wallet | Nova Web Portal (Chrome 120.0) | 1082240 | 0.9378455795387345 | 0.05165305292726197 | 0.010501367534003549 |
| E-Commerce | Nova App v4.2 (Android 14; Samsung S23) | 3669574 | 0.871418317221563 | 0.04153343140102911 | 0.08704825137740783 |
| E-Commerce | Nova App v4.2 (iOS 17.1; iPhone 14 Pro) | 3785129 | 0.8751006900953706 | 0.04040337859026733 | 0.08449593131436207 |
| E-Commerce | Nova Lite (Android Go) | 1563756 | 0.8597178843758233 | 0.04676049204607369 | 0.09352162357810298 |
| E-Commerce | Nova Web Portal (Chrome 120.0) | 1987368 | 0.8395571429146489 | 0.053828480684000146 | 0.10661437640135094 |
| Food Delivery | Nova App v4.2 (Android 14; Samsung S23) | 5210041 | 0.9403497976311511 | 0.03857589604381232 | 0.0210743063250366 |
| Food Delivery | Nova App v4.2 (iOS 17.1; iPhone 14 Pro) | 4797756 | 0.9442699878860034 | 0.03597515171676092 | 0.01975486039723571 |
| Food Delivery | Nova Lite (Android Go) | 2211921 | 0.9345274989477472 | 0.04206841021899064 | 0.02340409083326213 |
| Food Delivery | Nova Web Portal (Chrome 120.0) | 2644384 | 0.9163858199111778 | 0.05386509674842988 | 0.029749083340392318 |
| Grocery | Nova App v4.2 (Android 14; Samsung S23) | 2334843 | 0.9183157068805055 | 0.042697517563279413 | 0.03898677555621513 |
| Grocery | Nova App v4.2 (iOS 17.1; iPhone 14 Pro) | 2352112 | 0.9221784506860218 | 0.0407051194841062 | 0.037116429829872045 |
| Grocery | Nova Lite (Android Go) | 990613 | 0.9132708736913406 | 0.04564446458909786 | 0.04108466171956152 |
| Grocery | Nova Web Portal (Chrome 120.0) | 1237742 | 0.8952600784331468 | 0.05523445112147766 | 0.04950547044537553 |
| Ride Hailing | Nova App v4.2 (Android 14; Samsung S23) | 3908746 | 0.8834191323764706 | 0.08721109020642426 | 0.029369777417105128 |
| Ride Hailing | Nova App v4.2 (iOS 17.1; iPhone 14 Pro) | 3643866 | 0.8872263689169689 | 0.08426928981471876 | 0.02850434126831228 |
| Ride Hailing | Nova Lite (Android Go) | 1658378 | 0.8789690890737817 | 0.08977808436918483 | 0.03125282655703344 |
| Ride Hailing | Nova Web Portal (Chrome 120.0) | 1991741 | 0.8611671899107364 | 0.10287984230881425 | 0.03595296778044937 |

## Realism diagnostics

| metric | value |
| --- | --- |
| min_customer_activity_spread | 0.29894097698039884 |
| max_customer_non_completion_spread | 0.02693110538870444 |
| mean_category_share_std | 0.024100261211229313 |
| min_category_share_std | 0.015827283822687423 |
| mean_market_amount_std | 15.839120709447574 |
| mean_market_completion_std | 0.006990770443917461 |
| median_market_monthly_corr | 0.9899091162523939 |
| max_market_monthly_corr | 0.99997230856246 |

## Weather sensitivity diagnostics

| Category | bad_weather_days | normal_weather_days | bad_weather_avg_transactions | normal_weather_avg_transactions | bad_weather_avg_gmv_usd | normal_weather_avg_gmv_usd | bad_weather_avg_amount_usd | normal_weather_avg_amount_usd | bad_weather_completion_rate | normal_weather_completion_rate | bad_weather_transaction_lift | bad_weather_gmv_lift | bad_weather_avg_amount_lift | bad_weather_completion_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Digital Wallet | 2190 | 3666 | 1021.2283105022831 | 1029.8799781778505 | 47626.485529680365 | 47811.00006001091 | 49.5376810449177 | 49.27641279111509 | 0.9672316140545036 | 0.9669961299578695 | -0.008400656250133788 | -0.0038592485013689342 | 0.005302095647873817 | 0.00023548409663409764 |
| E-Commerce | 2190 | 3666 | 1891.9374429223744 | 1871.9268957992363 | 193101.6341826484 | 188373.30536824878 | 101.73138877382581 | 100.10333053248107 | 0.8629578599665388 | 0.8672953289331139 | 0.010689812282757165 | 0.025100843270527518 | 0.01626377696610685 | -0.004337468966575053 |
| Food Delivery | 2190 | 3666 | 2646.656621004566 | 2473.519912711402 | 77982.4240502283 | 70483.2445908347 | 31.076508837617915 | 29.944540117009858 | 0.9309527484166668 | 0.9428029690543778 | 0.06999608428596668 | 0.10639662664406858 | 0.037802174158789226 | -0.011850220637711018 |
| Grocery | 2190 | 3666 | 1198.766210045662 | 1170.2160392798692 | 94431.55223287671 | 85654.84743316966 | 80.58143085115394 | 74.683225085633 | 0.9104932961938156 | 0.9185612367448548 | 0.02439735041006805 | 0.10246594399172658 | 0.07897631307108073 | -0.00806794055103921 |
| Ride Hailing | 2190 | 3666 | 1989.9506849315069 | 1867.0864702673214 | 55562.48562557077 | 51982.36912711402 | 29.483337732143713 | 29.2467551348529 | 0.871358280950461 | 0.8880281501926198 | 0.0658053157262686 | 0.06887174552783823 | 0.00808919130344415 | -0.016669869242158852 |

## Fraud-like behavior diagnostics

| metric | value |
| --- | --- |
| burst_share | 0.0090235 |
| burst_non_complete_rate | 0.7395711198537153 |
| normal_user_hour_non_complete_rate | 0.08541641502094147 |
| non_complete_rate | 0.09131918 |
| high_amount_non_complete_rate | 0.13280701649139437 |
| proxy_suspicious_share | 0.01103472 |
| proxy_web_lite_share | 0.633688938187829 |
| baseline_web_lite_share | 0.3221363848081704 |
| proxy_promo_referral_share | 0.9554134586106399 |
| baseline_promo_referral_share | 0.5673594122535829 |
| new_at_risk_high_amount_non_complete_rate | 0.2417727487034418 |
| other_high_amount_non_complete_rate | 0.13044615240033178 |
| digital_wallet_proxy_share | 0.021227106318498078 |
| ecommerce_proxy_share | 0.01858515493656224 |
| other_category_proxy_share | 0.006657329695041344 |

## Notes

- BigQuery should ingest corrected parquet files from `data/corrected`, not `data/raw/`.
- BigQuery ingestion can use `data/corrected/nova_interactions.parquet` when a non-partitioned interactions file is required.
- QA parquet and CSV outputs are written under `data/corrected/qa`.
- Use strict mode for final readiness. Smoke runs can use `--no-strict` when row count or active-user thresholds are intentionally scaled down.
