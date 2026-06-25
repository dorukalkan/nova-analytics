---
icon: lucide/sprout
title: dbt Seeds
description: Nova analitik pipeline'ında kullanılan dış zenginleştirme verileri
---

# dbt Seeds

Seeds, Nova projesinin dış bağlam katmanıdır. Nova işlemlerini doğrudan açıklamaz; şehir pazarlarını ülke, hava durumu ve makroekonomik sinyallerle bağlayarak pazaryeri analizlerini zenginleştirir.

Pipeline içinde bu dosyalar `dbt seed` ile yüklenir, `stg_geo_*` modelleriyle staging katmanına alınır ve ardından pazaryeri ve talep analizi için intermediate ve mart modellerine join edilir.

Seed dosyaları Python fetch scriptleriyle dış API kaynaklarından ve gözden geçirilmiş lookup mantığından üretildi. Kaynak detayları ve API referansları için [API Kaynakları](../hakkinda/api-kaynaklari.md) sayfasına bakın.

!!! abstract "Katmanın amacı"

    Seed katmanı şu soruyu yanıtlar: Nova'nın iç pazaryeri verisini şehirler, ülkeler, hava durumu örüntüleri ve büyüme fırsatları arasında karşılaştırmadan önce hangi dış bağlama ihtiyaç var?

## Seed Girdileri

| Seed | Ne ekler | Ne için kullanılır |
| --- | --- | --- |
| `market_country_lookup` | Her Nova şehir pazarından ülke tanımlayıcılarına gözden geçirilmiş eşleme | Pazaryeri analizi, pazar fırsatı skoru, geo join'ler |
| `ext_weather_daily` | Nova pazarı bazında günlük 2024 Open-Meteo hava durumu | Talep etkenleri, hava duyarlılığı, saatlik/kategori talep yorumu |
| `ext_world_bank_indicators` | Nüfus, kişi başı GDP, kentleşme, internet kullanımı ve mobil abonelik gibi ülke düzeyi makro göstergeler | Pazar fırsatı skoru ve ülke bağlamı |
| `ext_country_metadata` | Bölge, para birimi, başkent ve zaman dilimi gibi REST Countries metadatası | Pazar etiketleme, ülke bağlamı, coğrafya zenginleştirme |

## Neden Önemli

Nova'nın ham platform verisi işlemlerin nerede gerçekleştiğini gösterebilir, ancak yerel bağlamı tek başına açıklayamaz. Seed katmanı projenin daha geniş iş soruları sormasını sağlar:

- hangi pazarların mevcut kullanımı güçlü, ancak makro büyüme alanı daha sınırlı;
- talebin yerel hava koşulları altında farklı davranıp davranmadığı;
- servis arzı, adoption ve ülke bağlamı birlikte değerlendirildiğinde pazar fırsatının nasıl değiştiği;
- coğrafi analizin şehir, ülke, bölge veya makro profil düzeyinde gruplanıp gruplanmaması gerektiği.

## Analiz Kapsamı

| Analiz sayfası | Seed katkısı |
| --- | --- |
| Pazaryeri Analizi | Ülke eşlemesi, makro göstergeler ve pazar bağlamı fırsat skorunu destekler |
| Yerel Talep Etkenleri | Hava durumu seedleri kötü hava etkisini, yağmur duyarlılığını ve talep feature engineering sürecini destekler |
| Yönetici Özeti | Dış bağlam büyümenin neden belirli pazarlarda yoğunlaştığını açıklamaya yardımcı olur |
