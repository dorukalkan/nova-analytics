# Corrected Nova Dataset Validation

Generated validation status: **PASS**

Input directory: `data/corrected`

Expected rows: `50,000,000`

Actual rows: `50,000,000`

## BigQuery readiness checks

| check | status | detail |
| --- | --- | --- |
| Exact target row count | PASS | 50,000,000 / 50,000,000 |
| Unique Transaction_UUID | PASS | 50,000,000 unique |
| All required columns present | PASS | all present |
| Zero nulls in required columns | PASS | 0 nulls |
| Full date coverage | PASS | 0 missing dates |
| Category matches service category | PASS | 0 mismatches |
| User FK coverage | PASS | 0 missing |
| Service FK coverage | PASS | 0 missing |
| Annual active user rate | PASS | 84.95% |
| Lifetime repeat user rate | PASS | 84.69% |
| Category amount spread | PASS | $62.25 |
| Completion rate spread | PASS | 12.36 pp |
| Hourly CV | PASS | 50.20% |
| December/January volume ratio | PASS | 1.71x |
| Top 1pct service share | PASS | 20.60% |
| Market GPS jitter bounds | PASS | 0.829 degrees |

## Monthly KPIs

| Month | n_transactions | active_users | total_amount_usd | completion_rate |
| --- | --- | --- | --- | --- |
| 2024-01-01 00:00:00 | 3300000 | 1046466 | 155153722.77 | 0.916869696969697 |
| 2024-02-01 00:00:00 | 3200000 | 1038283 | 150316360.91 | 0.916793125 |
| 2024-03-01 00:00:00 | 3500000 | 1079645 | 164680643.1 | 0.9167394285714285 |
| 2024-04-01 00:00:00 | 3700000 | 1109558 | 173886791.45 | 0.9170867567567568 |
| 2024-05-01 00:00:00 | 3900000 | 1136476 | 183188717.64 | 0.9166207692307692 |
| 2024-06-01 00:00:00 | 4050000 | 1158493 | 187626739.75 | 0.9166469135802469 |
| 2024-07-01 00:00:00 | 4200000 | 1182579 | 194897249.04 | 0.916867619047619 |
| 2024-08-01 00:00:00 | 4300000 | 1200183 | 199432297.72 | 0.9167362790697674 |
| 2024-09-01 00:00:00 | 4400000 | 1219219 | 206886228.25 | 0.9169704545454546 |
| 2024-10-01 00:00:00 | 4600000 | 1247659 | 216372668.02 | 0.9167308695652174 |
| 2024-11-01 00:00:00 | 5200000 | 1307510 | 275626743.01 | 0.9141076923076923 |
| 2024-12-01 00:00:00 | 5650000 | 1342215 | 294649163.53 | 0.9150355752212389 |

## Category KPIs

| Category | n_transactions | active_users | avg_amount_usd | median_amount_usd | completion_rate |
| --- | --- | --- | --- | --- | --- |
| Food Delivery | 14761005 | 1609691 | 26.92470988459119 | 24.67 | 0.9433671352323233 |
| E-Commerce | 11015252 | 1544827 | 88.51336887617278 | 65.34 | 0.8723223944400001 |
| Ride Hailing | 10898345 | 1537769 | 26.264548924630297 | 23.15 | 0.8882960669716365 |
| Grocery | 7287050 | 1411065 | 67.00711166109743 | 62.9 | 0.9184387372119033 |
| Digital Wallet | 6038348 | 1343351 | 42.35598808482055 | 23.72 | 0.9785204496329128 |

## Status by category and platform

| Category | Platform_User_Agent | n_transactions | completion_rate | failed_rate | refunded_rate |
| --- | --- | --- | --- | --- | --- |
| Digital Wallet | Nova App v4.2 (Android 14; Samsung S23) | 2085369 | 0.981291080859071 | 0.01681429042054428 | 0.0018946287203847377 |
| Digital Wallet | Nova App v4.2 (iOS 17.1; iPhone 14 Pro) | 2005787 | 0.981282658627262 | 0.016866696214503336 | 0.001850645158234648 |
| Digital Wallet | Nova Lite (Android Go) | 877800 | 0.9811084529505583 | 0.01707336523125997 | 0.0018181818181818182 |
| Digital Wallet | Nova Web Portal (Chrome 120.0) | 1069392 | 0.9658123494471625 | 0.030740832173795953 | 0.003446818379041549 |
| E-Commerce | Nova App v4.2 (Android 14; Samsung S23) | 3809482 | 0.8752308056580921 | 0.04001147662595597 | 0.08475771771595193 |
| E-Commerce | Nova App v4.2 (iOS 17.1; iPhone 14 Pro) | 3656429 | 0.8756800692697712 | 0.03992720766627767 | 0.0843927230639512 |
| E-Commerce | Nova Lite (Android Go) | 1603140 | 0.8755504821787242 | 0.04014621305687588 | 0.08430330476439986 |
| E-Commerce | Nova Web Portal (Chrome 120.0) | 1946201 | 0.8576621839162553 | 0.04559189929508822 | 0.09674591678865646 |
| Food Delivery | Nova App v4.2 (Android 14; Samsung S23) | 5107538 | 0.946509649071627 | 0.03478309901952761 | 0.01870725190884532 |
| Food Delivery | Nova App v4.2 (iOS 17.1; iPhone 14 Pro) | 4896799 | 0.9466902766480715 | 0.03471390187753265 | 0.018595821474395823 |
| Food Delivery | Nova Lite (Android Go) | 2148773 | 0.9463191318952723 | 0.03488316355427028 | 0.0187977045504574 |
| Food Delivery | Nova Web Portal (Chrome 120.0) | 2607895 | 0.9285404512068163 | 0.04650148874858842 | 0.024958060044595352 |
| Grocery | Nova App v4.2 (Android 14; Samsung S23) | 2521711 | 0.9214771240637805 | 0.040802058602274406 | 0.03772081733394509 |
| Grocery | Nova App v4.2 (iOS 17.1; iPhone 14 Pro) | 2418398 | 0.9218767961270229 | 0.04048258392539193 | 0.037640619947585136 |
| Grocery | Nova Lite (Android Go) | 1060203 | 0.9213131824754316 | 0.04071673066384456 | 0.03797008686072384 |
| Grocery | Nova Web Portal (Chrome 120.0) | 1286738 | 0.9036540461228315 | 0.050221568027057566 | 0.0461243858501109 |
| Ride Hailing | Nova App v4.2 (Android 14; Samsung S23) | 3766203 | 0.8917904850057207 | 0.0811475111670826 | 0.02706200382719678 |
| Ride Hailing | Nova App v4.2 (iOS 17.1; iPhone 14 Pro) | 3619625 | 0.8912555858687019 | 0.081475290948648 | 0.027269123182650137 |
| Ride Hailing | Nova Lite (Android Go) | 1585999 | 0.8912754673868016 | 0.08160723934882683 | 0.027117293264371543 |
| Ride Hailing | Nova Web Portal (Chrome 120.0) | 1926518 | 0.8734514808582116 | 0.09498328071681655 | 0.03156523842497189 |

## Notes

- BigQuery should ingest corrected parquet files from `data/corrected`, not `data/raw/`.
- QA parquet and CSV outputs are written under `data/corrected/qa`.
- Use strict mode for final readiness. Smoke runs can use `--no-strict` when row count or active-user thresholds are intentionally scaled down.
