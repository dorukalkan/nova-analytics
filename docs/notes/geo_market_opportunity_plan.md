---
icon: lucide/map
title: Geography analysis plan
description: Market opportunity and local demand driver plan for the Nova dashboard
---

# Geography Analysis Plan

=== "English"

    This note defines the proposed direction for the geography-focused part of the Nova analytics project. It is intentionally a planning document: implementation should happen step by step after each decision is reviewed.

    !!! note "Working title"

        **Geo Market Opportunity & Local Demand Drivers**

        The analysis asks: **Which Nova markets have the strongest expansion opportunity, and what local conditions help explain market-level demand?**

    ## Why this focus works

    The corrected Nova dataset now has a real market dimension, city coordinates, region labels, market weights, growth multipliers, iOS share, lifecycle segments, service tiers, category behavior, and daily transactions across 2024. That is enough to support a map-led Power BI report without forcing the story.

    The best framing is not "weather analysis" by itself. Weather should be one external feature family inside a broader market performance model.

    ```mermaid
    flowchart LR
        A[Nova transactions] --> D[Market-day feature table]
        B[Market dimension] --> D
        C[External context] --> D
        D --> E[Demand model]
        D --> F[Opportunity score]
        E --> G[Power BI model page]
        F --> H[Power BI market map]
    ```

    ## Business aims

    The analysis should answer three questions:

    1. **Where is Nova already strongest?**
       Compare markets by transactions, GMV, active users, growth, service supply, and reliability.

    2. **Where is there room to grow?**
       Compare Nova performance against market context such as country population, GDP per capita, urbanization, internet/mobile penetration, and device-market fit.

    3. **What drives daily demand locally?**
       Model demand using internal behavior plus external local conditions such as weather.

    !!! warning "Scope boundary"

        This track should stay market-led. Customer segmentation belongs to the customer track, and store/category performance belongs to the store/category track. This analysis may use customer, category, platform, promo, and service fields as explanatory features, but the headline story should remain geographic.

    ## Enrichment strategy

    === "Recommended hybrid"

        Use both macro context and weather, but for different jobs.

        - **Macro indicators** explain market opportunity.
        - **Weather indicators** explain daily demand variation.
        - Internal Nova features connect those external signals to actual platform performance.

    === "Macro-only option"

        Strong for business strategy, weaker for modeling because most macro fields are static at country level. With only 16 markets, this is better for scoring and segmentation than prediction.

    === "Weather-only option"

        Strong for modeling because weather varies by market and date, but too narrow as the whole business story unless tied back to expansion, operations, or demand planning.

    Recommended external sources:

    | Source | Use | Join grain | Why it helps |
    | --- | --- | --- | --- |
    | [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) | Daily temperature, rain, wind, weather code | market + date | Adds local daily variation for demand modeling |
    | [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures) | Population, GDP per capita, urbanization, internet/mobile indicators | country/year | Adds market potential context |
    | [REST Countries](https://restcountries.com/) | Country code, currency, region/subregion metadata | country | Useful for lightweight market metadata and documentation |

    ## Feature design

    The core analytical table should be a `market_category_day` mart. It gives enough rows for modeling without losing the geographic story.

    ```text title="Recommended modeling grain"
    one row = market + category + date
    expected size ~= 16 markets * 5 categories * 366 days = 29,280 rows
    ```

    Core fields:

    | Feature group | Examples |
    | --- | --- |
    | Market context | market, region, latitude, longitude, market weight, growth multiplier, configured iOS share |
    | Daily time | date, month, weekday, weekend flag, quarter, promo period share |
    | Demand target | transactions, GMV, active users, completed transactions |
    | Operational signals | completion rate, failed rate, refunded rate, platform mix, service tier mix |
    | Supply signals | active services, head service share, mid service share, long-tail service share |
    | Weather | mean temperature, max temperature, precipitation, rain flag, wind speed, weather code |
    | Macro context | population, GDP per capita, urbanization rate, internet/mobile indicator values |

    ??? info "Why not model at transaction level?"

        A 50M-row transaction-level model is unnecessary for the report. The dashboard needs market decisions, so aggregate to market-day or market-category-day. This keeps the model explainable and fast while preserving the business signal.

    ## Modeling plan

    Start simple and add complexity only if it improves the story.

    | Step | Model | Package | Purpose |
    | --- | --- | --- | --- |
    | 1 | Baseline average / seasonal benchmark | SQL or Python | Set a minimum bar |
    | 2 | Linear or Ridge regression | `scikit-learn` | Explain directional effects |
    | 3 | Random forest or histogram gradient boosting | `scikit-learn` | Capture nonlinear interactions |
    | 4 | Optional XGBoost model | `xgboost` | Use only if the sklearn model is too weak |
    | 5 | KMeans market clustering | `scikit-learn` | Segment markets for the map and strategy page |

    Recommended targets:

    - `market_category_daily_transactions`
    - `market_category_daily_gmv`
    - optional classification label: `high_demand_day`

    Recommended evaluation:

    - Use a time-based split: train on January through October 2024, validate on November and December 2024.
    - Compare baseline vs enriched model.
    - Report MAE, RMSE, and MAPE or WMAPE.
    - Show feature importance for interpretability.

    !!! note "Package recommendation"

        Add `scikit-learn` first. It covers regression, tree models, clustering, preprocessing, metrics, and feature importance. Keep `xgboost` optional so the project does not become package-heavy.

    ## Power BI report shape

    The geography track can fill a two-page report cleanly.

    ### Page 1: Market Opportunity Atlas

    Primary visuals:

    - Bubble map by market, sized by GMV or transactions and colored by opportunity segment.
    - Market leaderboard with transactions, GMV, active users, Jan-Dec growth, completion rate, and service supply.
    - Scatter plot of macro opportunity score vs Nova performance score.
    - Slicer by region and category.

    Main insight to support:

    ```text
    Which markets should Nova scale, fix, maintain, or monitor?
    ```

    ### Page 2: Local Demand Drivers

    Primary visuals:

    - Actual vs predicted demand by market/category.
    - Feature importance chart.
    - Weather sensitivity view, such as rain vs non-rain demand or temperature bands.
    - Matrix showing market-category demand patterns.

    Main insight to support:

    ```text
    Which local conditions and internal signals explain demand variation?
    ```

    ## Proposed implementation checkpoints

    Work should move in small reviewable steps.

    * [ ] Confirm final analysis question and page titles.
    * [ ] Build a country/market lookup for the 16 Nova markets.
    * [ ] Fetch and store weather data for each market and 2024 date.
    * [ ] Fetch or manually load macro indicators for each market country.
    * [ ] Create dbt marts for market-day and market-category-day features.
    * [ ] Prototype baseline and sklearn models in a notebook.
    * [ ] Export model predictions, feature importance, and market segments.
    * [ ] Build Power BI pages from final marts.

    !!! tip "Decision checkpoint after each step"

        After each checkpoint, inspect the output before moving on. The goal is to stay in control of the direction and avoid building a large pipeline before the analysis story is stable.

    ## Open decisions

    These should be decided before implementation starts:

    1. Should the main model target be transactions, GMV, or both?
    2. Should the dashboard rank markets by an explicit opportunity score, or show separate KPI rankings without a single score?
    3. Should weather be modeled globally across all markets, or should we also show category-specific weather sensitivity?
    4. Should macro indicators be fetched through an API script, loaded as a small seed table, or both?

    ## Default recommendation

    Use this default unless a later review changes direction:

    ```text
    Main grain: market_category_day
    Main target: daily transactions
    Secondary target: daily GMV
    Main model package: scikit-learn
    Optional advanced model: XGBoost
    Primary enrichment: Open-Meteo weather
    Secondary enrichment: World Bank macro indicators
    Power BI page 1: Market Opportunity Atlas
    Power BI page 2: Local Demand Drivers
    ```

=== "Türkçe"

    Bu not, Nova analytics projesindeki coğrafya odaklı analiz için önerilen yönü tanımlar. Bilerek bir plan dokümanı olarak tutulmuştur: uygulama, her karar gözden geçirildikten sonra adım adım ilerlemelidir.

    !!! note "Çalışma başlığı"

        **Coğrafi Pazar Fırsatı & Yerel Talep Sürücüleri**

        Analizin temel sorusu: **Nova için en güçlü büyüme fırsatı hangi pazarlarda, ve hangi yerel koşullar pazar seviyesindeki talebi açıklamaya yardımcı oluyor?**

    ## Bu odak neden uygun?

    Düzeltilmiş Nova veri setinde artık gerçek bir pazar boyutu, şehir koordinatları, bölge etiketleri, pazar ağırlıkları, büyüme çarpanları, iOS payı, yaşam döngüsü segmentleri, servis katmanları, kategori davranışı ve 2024 yılı boyunca günlük işlemler var. Bu yapı, hikayeyi zorlamadan harita merkezli bir Power BI raporunu desteklemek için yeterli.

    En iyi çerçeveleme sadece "hava durumu analizi" değil. Hava durumu, daha geniş bir pazar performansı modelinin içinde yer alan harici özellik gruplarından biri olmalı.

    ```mermaid
    flowchart LR
        A[Nova işlemleri] --> D[Pazar-gün özellik tablosu]
        B[Pazar boyutu] --> D
        C[Harici bağlam] --> D
        D --> E[Talep modeli]
        D --> F[Fırsat skoru]
        E --> G[Power BI model sayfası]
        F --> H[Power BI pazar haritası]
    ```

    ## İş hedefleri

    Analiz üç soruya cevap vermeli:

    1. **Nova şu anda nerede en güçlü?**
       Pazarları işlem sayısı, GMV, aktif kullanıcı, büyüme, servis arzı ve güvenilirlik üzerinden karşılaştır.

    2. **Nerede büyüme alanı var?**
       Nova performansını ülke nüfusu, kişi başı GSYH, kentleşme, internet/mobil penetrasyonu ve cihaz-pazar uyumu gibi pazar bağlamı göstergeleriyle karşılaştır.

    3. **Günlük yerel talebi ne yönlendiriyor?**
       Talebi, Nova iç davranışları ve hava durumu gibi harici yerel koşullarla modelle.

    !!! warning "Kapsam sınırı"

        Bu çalışma pazar odaklı kalmalı. Müşteri segmentasyonu müşteri konusuna, mağaza/kategori performansı ise mağaza-kategori konusuna ait. Bu analiz müşteri, kategori, platform, promosyon ve servis alanlarını açıklayıcı özellik olarak kullanabilir; ancak ana hikaye coğrafi kalmalı.

    ## Veri zenginleştirme stratejisi

    === "Önerilen hibrit yaklaşım"

        Makro bağlamı ve hava durumunu birlikte kullan, fakat farklı amaçlar için.

        - **Makro göstergeler** pazar fırsatını açıklar.
        - **Hava durumu göstergeleri** günlük talep değişimini açıklar.
        - Nova'nın iç özellikleri, harici sinyalleri gerçek platform performansına bağlar.

    === "Sadece makro seçeneği"

        İş stratejisi için güçlüdür, fakat modelleme için daha zayıftır çünkü makro alanların çoğu ülke seviyesinde statiktir. Sadece 16 pazar olduğu için bu yaklaşım tahminden çok skorlama ve segmentasyon için uygundur.

    === "Sadece hava durumu seçeneği"

        Hava durumu pazar ve tarihe göre değiştiği için modelleme açısından güçlüdür. Ancak genişleme, operasyon veya talep planlama hikayesine bağlanmazsa tek başına iş hikayesi olarak dar kalabilir.

    Önerilen harici kaynaklar:

    | Kaynak | Kullanım | Join seviyesi | Neden faydalı? |
    | --- | --- | --- | --- |
    | [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) | Günlük sıcaklık, yağmur, rüzgar, hava kodu | pazar + tarih | Talep modellemesi için yerel günlük değişkenlik ekler |
    | [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures) | Nüfus, kişi başı GSYH, kentleşme, internet/mobil göstergeleri | ülke/yıl | Pazar potansiyeli bağlamı ekler |
    | [REST Countries](https://restcountries.com/) | Ülke kodu, para birimi, bölge/alt bölge metadatası | ülke | Hafif pazar metadatası ve dokümantasyon için faydalıdır |

    ## Özellik tasarımı

    Temel analitik tablo `market_category_day` martı olmalı. Bu seviye, coğrafi hikayeyi kaybetmeden modelleme için yeterli satır sayısı verir.

    ```text title="Önerilen modelleme seviyesi"
    bir satır = pazar + kategori + tarih
    beklenen boyut ~= 16 pazar * 5 kategori * 366 gün = 29.280 satır
    ```

    Temel alanlar:

    | Özellik grubu | Örnekler |
    | --- | --- |
    | Pazar bağlamı | pazar, bölge, enlem, boylam, pazar ağırlığı, büyüme çarpanı, tanımlı iOS payı |
    | Günlük zaman | tarih, ay, haftanın günü, hafta sonu bayrağı, çeyrek, promosyon dönemi payı |
    | Talep hedefi | işlem sayısı, GMV, aktif kullanıcı, tamamlanan işlem sayısı |
    | Operasyonel sinyaller | tamamlanma oranı, başarısız oranı, iade oranı, platform karması, servis katmanı karması |
    | Arz sinyalleri | aktif servisler, head servis payı, mid servis payı, long-tail servis payı |
    | Hava durumu | ortalama sıcaklık, maksimum sıcaklık, yağış, yağmur bayrağı, rüzgar hızı, hava kodu |
    | Makro bağlam | nüfus, kişi başı GSYH, kentleşme oranı, internet/mobil gösterge değerleri |

    ??? info "Neden işlem seviyesinde model kurmuyoruz?"

        50 milyon satırlık işlem seviyesinde model bu rapor için gereksiz. Dashboard pazar kararlarına ihtiyaç duyuyor; bu yüzden pazar-gün veya pazar-kategori-gün seviyesine agregasyon daha doğru. Bu yaklaşım modeli açıklanabilir ve hızlı tutarken iş sinyalini korur.

    ## Modelleme planı

    Basit başla, karmaşıklığı sadece hikayeyi güçlendiriyorsa ekle.

    | Adım | Model | Paket | Amaç |
    | --- | --- | --- | --- |
    | 1 | Baz ortalama / sezonluk benchmark | SQL veya Python | Minimum başarı seviyesini belirlemek |
    | 2 | Linear veya Ridge regression | `scikit-learn` | Yönlü etkileri açıklamak |
    | 3 | Random forest veya histogram gradient boosting | `scikit-learn` | Doğrusal olmayan etkileşimleri yakalamak |
    | 4 | Opsiyonel XGBoost modeli | `xgboost` | Sadece sklearn modeli zayıf kalırsa kullanmak |
    | 5 | KMeans pazar kümeleme | `scikit-learn` | Harita ve strateji sayfası için pazarları segmente etmek |

    Önerilen hedefler:

    - `market_category_daily_transactions`
    - `market_category_daily_gmv`
    - opsiyonel sınıflandırma etiketi: `high_demand_day`

    Önerilen değerlendirme:

    - Zaman bazlı split kullan: Ocak-Ekim 2024 train, Kasım-Aralık 2024 validation.
    - Baseline modeli zenginleştirilmiş modelle karşılaştır.
    - MAE, RMSE ve MAPE veya WMAPE raporla.
    - Yorumlanabilirlik için feature importance göster.

    !!! note "Paket önerisi"

        Önce `scikit-learn` ekle. Regresyon, ağaç modelleri, kümeleme, preprocessing, metrikler ve feature importance için yeterli. `xgboost` opsiyonel kalsın; böylece proje gereksiz paket ağırlığı kazanmaz.

    ## Power BI rapor yapısı

    Coğrafya çalışması iki sayfalık bir raporu rahatça doldurabilir.

    ### Sayfa 1: Pazar Fırsatı Atlası

    Ana görseller:

    - GMV veya işlem sayısına göre boyutlanan, fırsat segmentine göre renklendirilen pazar bubble map.
    - İşlem sayısı, GMV, aktif kullanıcı, Ocak-Aralık büyümesi, tamamlanma oranı ve servis arzı içeren pazar lider tablosu.
    - Makro fırsat skoru ve Nova performans skoru scatter plotu.
    - Bölge ve kategori slicer'ı.

    Desteklenecek ana içgörü:

    ```text
    Nova hangi pazarları büyütmeli, düzeltmeli, korumalı veya izlemeli?
    ```

    ### Sayfa 2: Yerel Talep Sürücüleri

    Ana görseller:

    - Pazar/kategori bazında gerçek ve tahmin edilen talep.
    - Feature importance grafiği.
    - Yağmurlu ve yağmursuz günler veya sıcaklık bantları gibi hava duyarlılığı görünümü.
    - Pazar-kategori talep desenlerini gösteren matris.

    Desteklenecek ana içgörü:

    ```text
    Hangi yerel koşullar ve iç sinyaller talep değişimini açıklıyor?
    ```

    ## Önerilen uygulama kontrol noktaları

    Çalışma küçük ve gözden geçirilebilir adımlarla ilerlemeli.

    * [ ] Nihai analiz sorusunu ve sayfa başlıklarını netleştir.
    * [ ] 16 Nova pazarı için ülke/pazar lookup tablosu oluştur.
    * [ ] Her pazar ve 2024 tarihi için hava durumu verisini çek ve sakla.
    * [ ] Her pazar ülkesine ait makro göstergeleri çek veya küçük bir tablo olarak yükle.
    * [ ] Market-day ve market-category-day özellikleri için dbt martlarını oluştur.
    * [ ] Notebook içinde baseline ve sklearn modellerini prototiple.
    * [ ] Model tahminlerini, feature importance çıktısını ve pazar segmentlerini dışa aktar.
    * [ ] Final martlardan Power BI sayfalarını oluştur.

    !!! tip "Her adım sonrası karar kontrolü"

        Her kontrol noktasından sonra çıktıyı incele ve sonra ilerle. Amaç, analiz yönünü kontrol altında tutmak ve hikaye netleşmeden büyük bir pipeline kurmamak.

    ## Açık kararlar

    Uygulamaya başlamadan önce şu kararlar netleşmeli:

    1. Ana model hedefi işlem sayısı mı, GMV mi, yoksa ikisi birden mi olmalı?
    2. Dashboard pazarları tek bir fırsat skoruyla mı sıralamalı, yoksa ayrı KPI sıralamaları mı göstermeli?
    3. Hava durumu tüm pazarlar için global olarak mı modellenmeli, yoksa kategori bazlı hava duyarlılığı da gösterilmeli mi?
    4. Makro göstergeler API script'i ile mi çekilmeli, küçük bir seed tablo olarak mı yüklenmeli, yoksa ikisi birlikte mi kullanılmalı?

    ## Varsayılan öneri

    Sonraki bir incelemede yön değişmezse bu varsayılanla ilerle:

    ```text
    Ana seviye: market_category_day
    Ana hedef: günlük işlem sayısı
    İkincil hedef: günlük GMV
    Ana model paketi: scikit-learn
    Opsiyonel gelişmiş model: XGBoost
    Birincil zenginleştirme: Open-Meteo hava durumu
    İkincil zenginleştirme: World Bank makro göstergeleri
    Power BI sayfa 1: Pazar Fırsatı Atlası
    Power BI sayfa 2: Yerel Talep Sürücüleri
    ```
