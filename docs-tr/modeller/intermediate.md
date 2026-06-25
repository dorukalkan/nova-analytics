---
icon: lucide/package-open
title: Intermediate Modeller
description: Nova analizlerinin arkasındaki yeniden kullanılabilir dbt iş mantığı
---

# Intermediate dbt Modelleri

Intermediate modeller, temiz staging kaynaklarını ortak analitik yapı taşlarına dönüştürür. Amaç aynı metrikleri farklı dashboard veya sorgularda tekrar tekrar hesaplamamak, iş mantığını tek yerde tutmaktır.

Bu katman final dashboard kontratı değildir. Pazar bağlamı, tam tarih-kategori spine'ları, günlük talep metrikleri, servis sağlığı, müşteri metrikleri, RFM skorları ve tekrar davranışı özellikleri burada hazırlanır.

| Kullanım alanı | Örnek çıktı |
| --- | --- |
| Talep analizi | Pazar, kategori ve gün düzeyinde işlem ve hava durumu özellikleri. |
| Servis arzı | Pazar ve kategori bazında servis sayısı, kalite ve arz metrikleri. |
| Müşteri davranışı | Kullanıcı düzeyi işlem geçmişi, tekrar davranışı ve değer sinyalleri. |
| RFM | Recency, frequency ve monetary skorlarını besleyen ara metrikler. |
