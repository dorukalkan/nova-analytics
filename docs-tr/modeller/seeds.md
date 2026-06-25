---
icon: lucide/sprout
title: dbt Seeds
description: Nova analitik pipeline'ında kullanılan dış zenginleştirme verileri
---

# dbt Seeds

Seeds katmanı, Nova işlemlerinin dış bağlamını sağlar. Bu dosyalar doğrudan işlem verisi değildir; pazarları ülke, hava durumu ve makroekonomik sinyallerle zenginleştirir.

Seed dosyaları Python fetch scriptleriyle dış API kaynaklarından ve gözden geçirilmiş lookup mantığından üretildi. Kaynak detayları için [API Kaynakları](../hakkinda/api-kaynaklari.md) sayfasına bakılabilir.

| Seed | Amaç |
| --- | --- |
| `market_country_lookup` | Nova şehir pazarlarını ülke ve ISO kodlarıyla eşleştirir. |
| `ext_country_metadata` | Ülke metadatası, bölge, para birimi ve nüfus gibi alanları sağlar. |
| `ext_weather_daily` | Pazar bazında günlük hava durumu sinyalleri ekler. |
| `ext_world_bank_indicators` | Nüfus, GDP, kentleşme, internet kullanımı ve mobil abonelik gibi makro göstergeleri ekler. |
