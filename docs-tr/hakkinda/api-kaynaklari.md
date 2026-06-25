---
icon: lucide/cloud-download
title: API Kaynakları
description: Coğrafya ve pazar fırsatı analizi için kullanılan dış API kaynakları
---

# API Kaynakları

Nova işlem verisini pazar coğrafyası, tarihsel hava durumu, ülke metadatası ve makroekonomik bağlamla zenginleştirmek için dış API kaynakları kullandık. Bu kaynaklar işlemlerin yalnızca nerede gerçekleştiğini değil, hangi pazarların daha güçlü talep ve büyüme sinyalleri taşıdığını anlamaya yardımcı olur.

| Kaynak | Kullanım |
| --- | --- |
| [Open-Meteo](https://open-meteo.com/) | Pazar bazında günlük sıcaklık, yağış, yağmur, hava kodu ve rüzgar hızı sinyalleri. |
| [World Bank Open Data](https://data.worldbank.org/) | Nüfus, kişi başı GDP, kentleşme, internet kullanımı ve mobil abonelik gibi ülke göstergeleri. |
| [REST Countries](https://restcountries.com/) | ISO kodları, bölge, alt bölge, başkent, para birimi, nüfus ve zaman dilimi gibi ülke metadatası. |

Bu kaynaklardan üretilen dosyalar dbt seed olarak yüklenir ve staging/intermediate modeller üzerinden analiz martlarına taşınır.
