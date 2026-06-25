---
icon: lucide/package-search
title: Analitik Martlar
description: Analiz hazır dbt martları ve ML özellik çıktıları
---

# Analitik Martlar

Martlar Tableau dashboardları, notebooklar ve proje yazıları tarafından kullanılan final dbt kontratlarıdır. Ham veriden çok iş sorularına yakındırlar: pazar fırsatı, talep etkenleri, kategori sağlığı, müşteri segmentleri, tekrar davranışı ve işlem anomalisi incelemesi.

!!! abstract "Katmanın amacı"

    Mart katmanı şu soruyu yanıtlar: Tableau ve modelleme notebookları hangi temiz, analiz hazır tabloları tüketmeli?

## Pazaryeri Büyümesi

| Mart | Ne sağlar | Analiz çıktısı |
| --- | --- | --- |
| `mart_geo_market_opportunity` | Pazar seviyesi performans, büyüme, arz, makro, adoption, güvenilirlik ve fırsat skoru | Pazaryeri Analizi |

Bu mart, mevcut Nova performansını dış ülke bağlamı ve arz sinyalleriyle birleştirerek pazar fırsatı hikayesini destekler. Projenin "hangi pazarlar büyük?" sorusundan "hangi pazarlar çekici büyüme adayları?" sorusuna geçtiği yerdir.

## Talep Etkenleri ve Modelleme

| Mart | Ne sağlar | Analiz çıktısı |
| --- | --- | --- |
| `mart_geo_market_category_day_features` | Talep, hava durumu, takvim, makro, arz ve servis sinyalleriyle market-category-day feature tablosu | Talep modelleme notebooku, Yerel Talep Etkenleri |
| `mart_geo_weather_category_effects` | Kategori ve pazar bazında kötü hava işlem ve GMV artışı | Yerel Talep Etkenleri |
| `mart_geo_weather_category_sensitivity` | Yağmur duyarlılığı ve hava korelasyonu özeti | Yerel Talep Etkenleri, pazar kümelenmesi |
| `mart_geo_category_hourly_demand` | Pazar ve kategori bazında saatlik talep eğrileri | Yerel Talep Etkenleri |
| `mart_geo_market_cluster_features` | Stratejik kümelenme için pazar seviyesi feature tablosu | Yerel Talep Etkenleri |

Bu martlar talep etkenleri anlatısını destekler: hava durumu bazı kategorilerde önemlidir, ancak servis arzı ve pazar bağlamı talep resminin daha büyük bölümünü açıklar.

## Kategori ve Servis Performansı

| Mart | Ne sağlar | Analiz çıktısı |
| --- | --- | --- |
| `mart_category_performance` | Kategori seviyesi GMV, amount share, success, failure, refund, rating ve risk-segment sayıları | Kategori Performansı |
| `mart_category_market_performance` | Pazar kırılımında kategori performansı | Kategori Performansı |
| `mart_marketplace_service` | Servis seviyesi amount, reliability, rank ve risk segmenti | Kategori Performansı |
| `mart_service_monthly_performance` | Aylık servis sağlığı takibi | Kategori ve servis izleme |

Bu martlar kategori performansını operasyonel hale getirir. Yalnızca hangi kategorilerin büyük olduğunu değil; güvenilirlik kaçağı, refund, hata ve kritik servislerin nerede dikkat gerektirdiğini gösterir.

## Müşteri Segmentasyonu

| Mart | Ne sağlar | Analiz çıktısı |
| --- | --- | --- |
| `mart_customer_overview` | Müşteri profili, membership, acquisition, lifecycle, transaction count, completed revenue, average order value ve recency alanları | Müşteri Analizi |
| `mart_customer_segments` | Champions, Loyal Customers, Potential Loyalists, At Risk ve Lost Customers gibi RFM skorları ve iş dostu segmentler | RFM Analizi |

Bu martlar müşteri stratejisi sayfalarını destekler. Kullanıcı sayısını müşteri değerinden ayırarak hangi grupların elde tutulmaya, yükseltilmeye veya yeniden aktive edilmeye değer olduğunu gösterir.

## Tekrar ve Risk Analitiği

| Çıktı | Ne sağlar | Analiz çıktısı |
| --- | --- | --- |
| `mart_service_repeat_behavior` | Servis/kategori bazında repeat users, repeat interactions, repeat amount ve repeat dependency | Müşteri Tekrarı & Risk |
| `ml_transaction_fraud_features` | Anomali tespiti için işlem seviyesi davranış özellikleri | Fraud anomali notebooku |
| `ml_transaction_fraud_scores_sample` | Notebooktan yazılan Isolation Forest anomali skorları | Müşteri Tekrarı & Risk |
| `mart_transaction_fraud_tableau` | Anomali skorları ve suspicious flag'lerle birleştirilmiş Tableau hazır işlem bağlamı | Müşteri Tekrarı & Risk |

Risk workflow'u dbt ve notebook modellemesini birleştirir. dbt işlem seviyesi feature tablosunu oluşturur, notebook anomalileri skorlar ve final mart bu skorları inceleme için iş bağlamına geri bağlar.

!!! warning "Fraud yorumu"

    Fraud workflow'u denetimsiz anomali tespitidir. Çıktı, inceleme için şüpheli işlemleri işaretler; doğrulanmış fraud'u kanıtlamaz.

## Kalite Kontrolleri

Mart testleri benzersiz iş grain'lerini, zorunlu metrikleri, kabul edilen müşteri segment etiketlerini ve temel anomali skoru alanlarını kontrol eder. Özel dbt testleri ayrıca coğrafya grain'lerini ve market-day, category-day ve feature-mart toplamları arasındaki mutabakatı doğrular.

!!! success "Neden önemli"

    Martlar mühendislik ile hikayeleştirme arasındaki köprüdür. İş metrikleri tek seferlik dashboard hesaplamalarından değil, test edilmiş ve yeniden kullanılabilir modellerden geldiği için Tableau dashboardlarını ve proje yazılarını güvenilir kılar.
