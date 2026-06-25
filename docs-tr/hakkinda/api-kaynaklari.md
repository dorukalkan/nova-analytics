---
icon: lucide/cloud-download
title: API Kaynakları
description: Coğrafya ve pazar fırsatı analizi için kullanılan dış API kaynakları
---

# API Kaynakları

Nova işlem verisini pazar coğrafyası, tarihsel hava durumu, ülke metadatası ve makroekonomik bağlamla zenginleştirmek için dış API kaynakları kullandık. Bu kaynaklar bir işlem veri setini pazar fırsatı analizine dönüştürmeye yardımcı olur: yalnızca aktivitenin nerede gerçekleştiği değil, hangi pazarların daha güçlü talep sinyalleri, operasyon koşulları ve büyüme bağlamı taşıdığı görülebilir.

## Kullanılan Kaynaklar

| Kaynak | API dokümantasyonu | Nasıl kullandık |
| --- | --- | --- |
| [Open-Meteo](https://open-meteo.com/) | [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) | Sıcaklık, precipitation, rain, weather code ve wind speed gibi günlük pazar seviyesi hava durumu sinyalleri ekledik. Open-Meteo bu API'yi ERA5, ERA5-Land ve ECMWF IFS gibi model kaynaklarından gelen reanalysis tabanlı tarihsel hava durumu verisi olarak dokümante eder. |
| [World Bank Open Data](https://data.worldbank.org/) | [Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation) | Nüfus, kişi başı GDP, kentleşme, internet kullanımı ve mobil abonelikler gibi ülke seviyesi makro göstergeler ekledik. World Bank veri setleri açık veri lisansları altında yayınlanır ve yeniden kullanımda atıf beklenir. |
| [REST Countries](https://restcountries.com/)[^1] | [REST Countries docs](https://restcountries.com/docs) | ISO kodları, bölge, alt bölge, başkent, para birimi, nüfus ve zaman dilimleri gibi ülke metadatası ekledik. REST Countries ülke alanlarını public registry'ler, çok taraflı kurumlar ve açık veri projelerinden derler. |

Bu API'ler yalnızca analitik zenginleştirme için kullanılır. Final pazar fırsatı analizi, rapor veya dashboard içinde gösterilen herhangi bir dış metrik için ilgili kaynak sayfayı yine de cite etmelidir.

[^1]: REST Countries tam erişim için API key gerektirir. Open-Meteo ve World Bank Indicators API bu projede kullanılan çağrılar için API key gerektirmedi.
