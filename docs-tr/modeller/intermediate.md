---
icon: lucide/package-open
title: Intermediate Modeller
description: Nova analizlerinin arkasındaki yeniden kullanılabilir dbt iş mantığı
---

# Intermediate dbt Modelleri

Intermediate modeller, Nova projesinin yeniden kullanılabilir mantık katmanıdır. Temiz staging kaynaklarını ortak analitik yapı taşlarına dönüştürür: pazar bağlamı, eksiksiz tarih/kategori spine'ları, günlük talep metrikleri, servis sağlığı, müşteri metrikleri, RFM skorları ve tekrar davranışı özellikleri.

Bu modeller final dashboard kontratı değildir. Görevleri final martları tutarlı, test edilmiş ve yorumlaması daha kolay hale getirmektir.

!!! abstract "Katmanın amacı"

    Intermediate katmanı şu soruyu yanıtlar: Her dashboard ve notebook'un aynı hesaplamaları kullanması için hangi yeniden kullanılabilir iş mantığı bir kez tanımlanmalı?

## Pazar Bağlamı ve Takvim Mantığı

| Modeller | Ne yapar | Nerede kullanılır |
| --- | --- | --- |
| `int_geo_country_macro_pivot` | Long-form World Bank göstergelerini ülke başına tek satıra pivot eder | Pazaryeri Analizi |
| `int_geo_market_context` | Nova pazar alanlarını, ülke eşlemesini, ülke metadatasını ve makro göstergeleri birleştirir | Pazaryeri Analizi, Talep Etkenleri |
| `int_geo_date_spine` | Hava durumu tarih aralığından eksiksiz takvim spine'ı oluşturur | Talep Etkenleri |

Bu grup pazar analizini karşılaştırılabilir hale getirir. Her şehri yalnızca işlem etiketi olarak görmek yerine pipeline her pazara ülke, makro, takvim ve coğrafya bağlamı verir.

## Talep Temelleri

| Modeller | Ne yapar | Nerede kullanılır |
| --- | --- | --- |
| `int_geo_market_day_metrics` | İşlemleri market-day düzeyinde demand, GMV, activity, status, promo ve platform metriklerine agregeler | Pazaryeri Analizi |
| `int_geo_market_category_day_metrics` | İşlemleri market-category-day metriklerine agregeler | Talep Etkenleri, talep modellemesi |
| `int_geo_market_category_hour_metrics` | Kategori talebini pazar ve saat bazında agregeler | Talep Etkenleri |
| `int_geo_market_category_spine` | Eksik talep açıkça görülsün diye eksiksiz market/category/date grid'i oluşturur | Talep Etkenleri |
| `int_geo_service_supply_by_market_category` | Aktif servisler, rating, popularity ve service-tier karışımı gibi arz tarafı bağlamı ekler | Pazaryeri Analizi, Talep Etkenleri |

Bu grup talep etkenleri çalışmasının analitik tabanıdır. Projenin talebi hava durumu, zaman, servis arzı, pazar bağlamı ve kategori davranışıyla tutarlı grain'lerde karşılaştırmasını sağlar.

## Servis ve Kategori Sağlığı

| Modeller | Ne yapar | Nerede kullanılır |
| --- | --- | --- |
| `int_services_enriched` | Servislere pazar ve ülke bağlamı ekler | Kategori Performansı, Müşteri Tekrarı & Risk |
| `int_service_interactions` | İşlemleri zenginleştirilmiş servis bağlamıyla birleştirir | Kategori Performansı, tekrar davranışı, fraud features |
| `int_service_health` | Servis seviyesi interaction, amount, success, failure, refund ve rating metriklerini hesaplar | Kategori Performansı |
| `int_service_risk` | Success, failure, refund ve rating sinyalleriyle servisleri risk segmentlerine ayırır | Kategori Performansı |
| `int_category_health` | Servis sağlığını kategori seviyesi performansa taşır | Kategori Performansı |
| `int_service_monthly_health` | Servis performansını zaman içinde takip eder | Kategori ve servis performansı izleme |

Bu grup ham servis aktivitesini operasyonel zekaya dönüştürür. Kategori sayfasının ana sorusunu destekler: hangi kategoriler büyük, güvenilir, riskli veya büyümeden önce stabilize edilmeye değer?

## Müşteri, RFM ve Tekrar Mantığı

| Modeller | Ne yapar | Nerede kullanılır |
| --- | --- | --- |
| `int_customer_metrics` | Müşteri düzeyi transaction count, spend, order dates, lifetime, category count ve service usage oluşturur | RFM Analizi |
| `int_rfm_features` | Müşteri geçmişini recency, frequency ve monetary alanlarına dönüştürür | RFM Analizi |
| `int_rfm_scores` | Segment etiketleri için kullanılan 1-5 RFM skorları atar | RFM Analizi |
| `int_user_service_repeat_behavior` | User-service grain'inde tekrar davranışını ölçer | Müşteri Tekrarı & Risk |

Bu grup işlem geçmişini müşteri stratejisine çevirir. Segmentasyon, retention önceliklendirmesi ve repeat-use metriklerini dashboard-only hesaplamalara ihtiyaç duymadan besler.

## Kalite Kontrolleri

Intermediate testleri grain ve ilişkilere odaklanır: market-day, market-category-day, market-category-hour, market-category-date spine satırı ve market-category supply satırı başına tek kayıt. Bu kontroller önemlidir; çünkü final dashboardlar ve notebooklar her intermediate modelin stabil grain'e sahip olduğunu varsayar.

!!! tip "Neden önemli"

    Intermediate katman, projenin grafikler toplamı değil bir pipeline haline geldiği yerdir. Talep, arz, servis sağlığı ve müşteri davranışı için ortak tanımlar final analiz sayfalarını tutarlı tutar.
