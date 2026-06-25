---
icon: lucide/arrows-up-from-line
title: Staging Modelleri
description: Nova analitiği için temiz kaynak arayüzleri
---

# Staging Modelleri

Staging modelleri ham/düzeltilmiş veri ile analiz pipeline'ı arasındaki temiz arayüzdür. İsimleri standartlaştırır, kaynak grain'ini korur ve business scoring mantığı eklemeden temel validasyon sağlar.

Portföy okuyucusu için önemli nokta basittir: her analiz sayfası, ham alanları dashboard sorguları içinde tekrar tekrar temizlemek yerine stabil bir kaynak-facing model setinden başlar.

!!! abstract "Katmanın amacı"

    Staging katmanı şu soruyu yanıtlar: Projenin geri kalanı tutarlı transaction, user, service, market ve external-context alanlarına güvenebilir mi?

## Nova Çekirdek Varlıkları

| Model | Grain | Pipeline rolü | Desteklediği ana analizler |
| --- | --- | --- | --- |
| `stg_interactions` | işlem başına bir satır | Transaction amount, status, timestamp, category, market, user, service, platform, lifecycle ve promo alanlarını standartlaştırır | Yönetici Özeti, Pazaryeri, Talep Etkenleri, Kategori Performansı, Müşteri/RFM, Tekrar & Risk |
| `stg_users` | kullanıcı başına bir satır | Membership, acquisition, lifecycle, device, market ve join-date alanlarını standartlaştırır | Müşteri Analizi, RFM Analizi, Müşteri Tekrarı & Risk |
| `stg_services` | servis başına bir satır | Category, rating, market, service tier ve popularity alanlarını standartlaştırır | Kategori Performansı, Talep Etkenleri, service supply features |
| `stg_markets` | pazar başına bir satır | Şehir pazarı adları, bölgeler, koordinatlar ve pazar konfigürasyon alanlarını standartlaştırır | Pazaryeri Analizi, Talep Etkenleri, pazar kümelenmesi |

## Dış Bağlam Staging

| Model | Grain | Pipeline rolü | Desteklediği ana analizler |
| --- | --- | --- | --- |
| `stg_geo_market_country_lookup` | Nova pazarı başına bir satır | Nova şehir pazarlarını ülke tanımlayıcılarına bağlar | Pazaryeri Analizi, Talep Etkenleri |
| `stg_geo_weather_daily` | pazar ve gün başına bir satır | Günlük yerel hava durumu özellikleri ekler | Talep Etkenleri, hava duyarlılığı |
| `stg_geo_world_bank_indicators` | ülke ve gösterge başına bir satır | Pivot öncesinde makro göstergeleri sağlar | Pazaryeri fırsat skoru |
| `stg_geo_country_metadata` | ülke başına bir satır | Ülke etiketleri, para birimi, bölge ve zaman dilimi bağlamı ekler | Pazaryeri Analizi ve dashboard etiketleme |

## İş Açısından Değeri

Staging katmanı iş mantığının dashboardlara dağılmasını engeller. Örneğin kategori adları, işlem durumları, service tier'ları ve user lifecycle alanları bir kez standartlaştırılır, sonra proje boyunca yeniden kullanılır. Bu da analizleri daha güvenilir ve açıklanabilir hale getirir.

## Kalite Kontrolleri

Staging testleri temel konuları kapsar: benzersiz transaction, user, service ve market anahtarları; category, status, user segment ve service tier için kabul edilen değerler; zorunlu timestamp ve date alanları; işlemlerden kullanıcı ve servislere ilişkiler. Bu testler veri iş metriklerine agreglenmeden önce ilk kalite kapısıdır.
