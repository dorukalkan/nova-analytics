# Nova Sentetik Veri Denetimi

Bu rapor, `notebooks/nova_exploration.ipynb` dosyasını ve ham parquet tablolarını dashboard bakış açısıyla inceler. Veri yapısal olarak temiz, ancak bazı alanlar Power BI grafiklerini düz ya da yanıltıcı gösterecek kadar sentetik davranıyor. Bu nedenle proje, bir analytics correction layer eklemeden ilerlememeli.

## Yönetici özeti

Raw tabloları değiştirilemez bir sentetik kaynak olarak ele alıp gerçekçi olmayan davranışları düzelten curated marts oluşturursak, veri seti final analytics projesi için kullanılabilir. Notebook'un mevcut KPI parquet çıktılarından doğrudan final görseller üretmek güvenli değildir.

En yüksek riskli konular:

- Interaction `Category`, `services.Category` ile `50,000,000` satırın `40,018,166` tanesinde, yani `80.04%` oranında uyuşmuyor.
- Aylık hacim neredeyse tamamen aydaki gün sayısıyla açıklanıyor; `2024-12-31` eksik.
- Saatlik transaction hacmi 24 saatin tamamında neredeyse düz.
- `Amount_USD`, `$5` ile `$150` arasında uniform dağılıyor ve category, status, platform ve referral source kırılımlarında neredeyse aynı dağılıma sahip.
- `Status`, her dimension genelinde yaklaşık `90% Completed`, `5% Failed`, `5% Refunded` seviyesinde sabit.
- Platform, referral source, category, amount, status, service, GPS ve user attribute alanları çoğunlukla birbirinden bağımsız davranıyor.
- 2M kullanıcının tamamı active ve repeat user; bu yüzden lifetime retention ve cross-sell metrikleri mevcut haliyle anlamlı değil.

## Notebook bölümlerine göre inceleme

### Cells 2-9: loading and schema

Bu hücreler teknik olarak doğru. 2.6 GiB interaction tablosu için Polars lazy scanning doğru yaklaşım. Notebook bu alanları türetilmiş gibi anlatsa da raw interaction tablosu zaten `Timestamp_dt`, `Date`, `Month` ve `Hour` içeriyor.

Risk: Raw schema içinde `Timestamp` string, `Timestamp_dt` ise typed. BigQuery tarafında ikisini de ingest edebiliriz, ancak downstream modellerde tek bir typed timestamp üzerinde standartlaşmalıyız.

### Cells 12-17: counts, keys, and nulls

Veri temel kalite kontrollerinden kusursuz geçiyor:

- 50M interaction rows.
- 50M unique transaction UUIDs.
- 2M unique users.
- 50k unique services.
- Her tabloda sıfır null.

Bu temizlik iyi, ancak fazla kusursuz. Bu kontrolleri dbt tests olarak koruyun, fakat synthetic-behavior tests de ekleyin. Aksi halde null/uniqueness kontrolleri tek başına veri setini analitik açıdan olduğundan daha sağlıklı gösterecek.

Önerilen testler:

- `Transaction_UUID` unique and not null.
- `User_ID` ve `Service_ID` relationship tests.
- `Status`, `Category`, `Membership_Tier`, `Primary_Device` için accepted values.
- Category mismatch rate, eksik `2024-12-31`, flat hourly coefficient of variation ve GPS/global-uniform behavior için custom warning tests.

### Cells 20-24: categorical profiling

Category ve status oranları hedeflenmiş gibi görünüyor:

- Category: Food Delivery `40.01%`, Ride Hailing `20.00%`, E-Commerce `20.00%`, Grocery `10.00%`, Digital Wallet `10.00%`.
- Status: Completed `90.00%`, Refunded `5.00%`, Failed `5.00%`.
- Platform: dört user agent neredeyse tam olarak `25%`.
- Referral source: beş kaynak neredeyse tam olarak `20%`.

Bu alanlar faydalı segmentation için fazla bağımsız ve fazla dengeli. Geniş dashboard slice'ları için kullanılabilirler, fakat segmentler arası farklar adjusted edilmeden business finding olarak yorumlanmamalı.

### Cell 29: service/category consistency

Bu en önemli sorun. Fact table category ile service dimension category çoğunlukla ilişkisiz:

- Rows checked: `50,000,000`
- Missing service matches: `0`
- Category mismatches: `40,018,166`

Mevcut downstream etkisi:

- `category_kpis`, her category için `active_services = 50,000` raporluyor.
- Bir merchant, service dimension category ile çelişen transaction categories altında görünebiliyor.
- Power BI içinde merchant/category drilldown görselleri yanıltıcı olacak.

Önerilen kural: Her dashboard page için tek bir category kaynağı seçin.

- Executive category page: `interactions.Category` alanını `transaction_category` olarak kullanın.
- Merchant/service page: `services.Category` alanını `service_category` olarak kullanın.
- Bir correction layer service IDs veya category labels remap etmedikçe ikisini aynı hiyerarşide birleştirmeyin.

### Cells 31-32: sample export

Sample deterministic ve prototyping için faydalı. `SAMPLE_MOD = 1000` yaklaşık `0.1%` üretir, `1%` değil; bu yüzden `interactions_sample_0_1pct.parquet` dosya adı doğru.

Risk: Sample row-random olduğu için sentetik düzlüğü korur. Performance testing için uygundur, gerçekçi chart behavior değerlendirmek için uygun değildir.

### Cells 35-37: monthly KPIs and charts

Aylık transaction counts, aydaki gün sayısına göre ayarlanınca düzleşiyor. Daily counts ortalama yaklaşık `136,986`; coefficient of variation yalnızca `0.27%`.

`2024-12-31` eksik olduğu için December 30 günlük bir ay gibi görünüyor. Aylık line chart içinde görünen değişimler business seasonality'den çok 29/30/31 günlük ay uzunluklarını yansıtıyor.

Önerilen dashboard düzeltmesi:

- Calendar/date dimension ekleyin.
- Deterministic `demand_weight` içeren weighted daily ve monthly marts oluşturun.
- Weekday, seasonality, holiday, campaign ve category-specific factors ekleyin.
- QA sırasında hem `raw_transactions` hem `adjusted_transactions` gösterin; final storytelling için adjusted metrics kullanın.

### Cells 39-42: category KPIs

Category transaction share basit bir market-mix hikayesini destekleyebilir, ancak fixed probabilities ile üretilmiş. Average amount, completion rate ve active users category kırılımlarında neredeyse aynı.

Mevcut chart riski:

- Category bar chart'ları yalnızca fixed category weights farklı olduğu için makul görünecek.
- Category trend lines mekanik olarak paralel ve oransal ilerleyecek.
- Active service counts, category/service mismatch nedeniyle geçersiz.

Önerilen düzeltme:

- Category-specific adjusted amount distributions üretin.
- Category-specific hourly ve weekday curves üretin.
- Category KPIs içindeki `active_services` metriğini transaction category veya service category kaynaklarından biriyle tutarlı bir corrected metric ile değiştirin.

### Cells 44-50: status, referral, platform, hourly KPIs

Bu tablolar yapısal olarak faydalı, ancak analitik olarak düz:

- Completion rates her category, platform, referral source ve hour için yaklaşık `90%`.
- Referral sources her category içinde yaklaşık `20%` katkı veriyor.
- Platform user agents yaklaşık `25%` katkı veriyor.
- Hourly counts category içinde yalnızca yaklaşık `0.1%` ile `0.24%` arasında değişiyor.

Önerilen düzeltme:

- `Referral_Source` alanını per-transaction truth olarak değil, generated user acquisition source olarak ele alın ya da `Touchpoint_Source` olarak yeniden adlandırın.
- Platform değerlerini `users.Primary_Device` alanına conditional üretin.
- Completion/refund/failure outcomes değerlerini category, platform, hour, amount, service rating ve referral source üzerinden üretin.

### Cell 53: service performance

Service KPIs mevcut haliyle gerçek merchant performance ranking için kullanışlı değil.

Gözlenen pattern:

- 50,000 services.
- Mean transactions per service: tam olarak `1,000`.
- Service transaction count coefficient of variation: `3.16%`.
- Top services çoğunlukla random noise.
- Transactions per active user per service neredeyse her zaman `1.0`.

Önerilen düzeltme:

- Merchant popularity tiers veya Pareto/lognormal merchant demand factor ekleyin.
- Service completion rate değerini `Rating`, category ve platform ile ilişkilendirin.
- Mevcut top merchant rankings değerlerini business finding olarak sunmayın.

### Cells 55-63: user lifecycle, cross-sell, and ML features

Lifetime user activity retention veya cross-sell analysis için fazla uniform:

- 2M kullanıcının tamamında activity var.
- Average transactions per user tam olarak `25`.
- Median transactions per user `25`.
- Repeat user rate `1.0`.
- Multi-service user rate `1.0`.
- Join-month cohort metrics tüm 2023 cohort'larında neredeyse aynı.
- Kullanıcıların `83.16%` kadarı 5 category'nin tamamını kullanıyor.

Önerilen düzeltme:

- Lifetime `repeat_user_rate` ve `multi_service_user_rate` metriklerini headline KPI olarak kullanmayın.
- Repeat users tanımını reporting period bazında yeniden yapın; örneğin seçilen ayda en az 2 transaction yapan users.
- Inactive users, low-activity users, loyal users, dormant users ve high-value users içeren generated user lifecycle layer oluşturun.
- ML için mevcut `is_repeat_user` veya `is_multi_service_user` label'larını modellemeyin; çünkü neredeyse sabitler.

## Field-level trust matrix

| Field or metric | Mevcut haliyle güvenilir mi? | Reason | Dashboard guidance |
|---|---:|---|---|
| Transaction UUID | Evet | Unique and complete | Transaction key olarak kullan |
| User ID | Evet | Complete FK coverage | User key olarak kullan |
| Service ID | Kısmen | Complete FK, but category contradiction | Merchant pages içinde dikkatli kullan |
| Timestamp/Date | Kısmen | Valid, but uniform and missing Dec 31 | Calendar weighting veya adjusted timestamp logic ekle |
| Category | Kısmen | Useful labels, fixed shares, contradicts service category | Yalnızca transaction category olarak kullan |
| Amount USD | Hayır | Uniform 5-150 across all groups | Adjusted amount oluştur |
| Status | Hayır | Fixed 90/5/5 everywhere | Adjusted status oluştur |
| Platform user agent | Hayır | Independent of primary device | Adjusted platform/channel oluştur |
| Referral source | Hayır | Uniform per transaction | User acquisition source veya campaign layer oluştur |
| GPS | Hayır | Uniform over globe, many impossible business locations | Synthetic market/city dimension ile değiştir |
| Membership tier | Kısmen | Plausible 80/15/5 split, but weakly related to behavior | Behavioral effects üretildikten sonra kullan |
| Service rating | Kısmen | Ratings are uniformly distributed 3.0-5.0 | Yalnızca reliability/volume ile ilişkilendirdikten sonra kullan |

## Önerilen correction architecture

Raw parquet dosyalarını BigQuery içine değiştirmeden yükleyin:

```text
raw_nova.interactions
raw_nova.users
raw_nova.services
```

Sonra curated dbt models oluşturun:

```text
staging/
  stg_nova__interactions.sql
  stg_nova__users.sql
  stg_nova__services.sql

intermediate/
  int_nova__calendar_factors.sql
  int_nova__user_segments.sql
  int_nova__service_popularity.sql
  int_nova__transaction_adjustments.sql

marts/
  fct_transactions_curated.sql
  dim_users_curated.sql
  dim_services_curated.sql
  dim_markets.sql
  mart_executive_daily.sql
  mart_category_performance.sql
  mart_user_lifecycle.sql
  mart_service_reliability.sql
```

Curated fact table raw fields değerlerini korumalı ve adjusted fields eklemeli:

```text
raw_amount_usd
adjusted_amount_usd
raw_status
adjusted_status
transaction_category
service_category
category_match_flag
raw_platform_user_agent
adjusted_platform
raw_referral_source
user_acquisition_source
market_id
demand_weight
```

## Pratik fix recipes

### 1. Category and service consistency

Conservative option:

- Raw `Service_ID` değerini koruyun.
- Fact category alanını `transaction_category` olarak yeniden adlandırın.
- Dimension category alanını `service_category` olarak yeniden adlandırın.
- `category_match_flag` ekleyin.
- Matching rows ile filtrelenmedikçe category-to-service drilldown görsellerinden kaçının.

More realistic option:

- Category bazında deterministic service remapping table oluşturun.
- Mismatched rows için `Transaction_UUID` hash'i kullanarak aynı transaction category içindeki services arasından bir `analytics_service_id` atayın.
- Lineage için raw `Service_ID` değerini koruyun.

### 2. Time-series realism

`demand_weight` değerini şunlardan üretin:

- Weekday effect: business-like categories için hafta sonları daha düşük, food/e-commerce için hafta sonları daha yüksek.
- Hour-of-day effect: food için lunch/dinner peaks, ride hailing için commute peaks, e-commerce için evening peaks.
- Month effect: holidays ve campaign periods.
- Category effect: her category farklı profile sahip olmalı.

Marts içinde kullanımı:

```text
adjusted_transactions = sum(demand_weight)
adjusted_gmv = sum(adjusted_amount_usd * demand_weight)
```

### 3. Amount realism

Düz amount chart'larını category-specific distributions ile üretilmiş `adjusted_amount_usd` ile değiştirin:

- Food Delivery: lower ticket size, lunch/dinner multiplier.
- Grocery: medium-to-high basket size.
- Ride Hailing: distance/time proxy, commute multiplier.
- E-Commerce: long-tailed basket size.
- Digital Wallet: mixed small payments plus larger transfers.

`raw_amount_usd` yalnızca audit için kalsın.

### 4. Status realism

Adjusted status değerini şu faktörlerin yönettiği probabilities ile üretin:

- Platform/channel.
- Category.
- Hour.
- Amount bucket.
- Service rating.
- User segment.

Örnek beklentiler:

- Web, native apps'e göre biraz daha yüksek failure gösterebilir.
- Low-rated services daha yüksek refund/failure gösterebilir.
- E-commerce, food'a göre daha yüksek refund rate gösterebilir.
- Digital wallet için failure behavior ile refund behavior farklı olabilir.

### 5. Referral and platform realism

Referral genellikle her transaction üzerinde bağımsız bir değer değil, user-level acquisition olmalı.

Önerilen curated fields:

- `dim_users_curated` üzerinde `user_acquisition_source`.
- Campaign interactions gerekiyorsa transactions üzerinde `touchpoint_source`.

Platform conditional olmalı:

- iOS primary users çoğunlukla iOS app veya web üzerinden transact etmeli.
- Android primary users çoğunlukla Android app, Lite veya web üzerinden transact etmeli.
- Web her ikisi için de mevcut olmalı.

### 6. Geography

Map visuals için raw GPS kullanmayın. Latitude/longitude üzerinde uniform dağılıyor ve activity değerlerini oceans, poles ve unserved regions içine yerleştirecek.

Bunun yerine `dim_markets` oluşturun:

- Users için 8-20 synthetic cities/markets atayın.
- Her market için realistic lat/long centroids verin.
- Market-level demand factors ekleyin.
- Point maps gerekiyorsa yalnızca jitter kullanın.

### 7. User lifecycle

Mevcut lifetime user labels analitik olarak kullanışlı değil. Dashboarding öncesinde user segments oluşturun:

- New/infrequent users.
- Active regular users.
- Power users.
- Dormant users.
- High-value users.
- Category specialists.
- Multi-category adopters.

Period-based definitions kullanın:

- Monthly active users.
- Monthly repeat users.
- 30/60/90-day retained users.
- Current month ve previous month içinde active olan users.

## Dashboard önerisi

Fix'lerden sonra en iyi final dashboard açısı:

1. Adjusted daily/monthly volume, GMV, active users ve completion rate içeren executive performance overview.
2. Adjusted amount/status/hourly patterns kullanan category performance page.
3. Adjusted status ve service rating effects kullanan reliability page.
4. Generated/period-based segments kullanan user lifecycle page.

Mevcut haliyle kaçınılacaklar:

- Global GPS map.
- Mevcut `service_kpis` tablosuna dayalı merchant leaderboard.
- Lifetime repeat user rate.
- Lifetime multi-service user rate.
- Raw `Amount_USD` üzerinden avg amount by category/status/platform.
- Raw `Status` üzerinden completion rate comparisons.

