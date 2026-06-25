---
icon: lucide/cloud-sun
title: Yerel Talep Etkenleri
description: Yerel kategori talebinin arkasındaki hava durumu, pazar bağlamı, servis arzı ve zamanlama sinyalleri
author: Doruk Alkan
---

# Yerel Talep Etkenleri

![Tableau Talep Etkenleri Dashboard'u](../assets/3_demand.png)

=== "İçgörüler"

    !!! note "İş özeti"

        Ekstrem hava koşulları yemek siparişi ve taksi çağırma gibi kategorilerde yaklaşık **%7** pozitif etki gösterebilir; ancak geniş modelde talebi açıklayan en güçlü sinyal servis arzı ve servis kalitesidir.

    ## İş İçgörüleri

    - Servis arzı özellikleri modele eklendiğinde tahmin kalitesi belirgin biçimde artar; kaliteli restoran, sürücü ve servis deneyimi talep artışıyla ilişkilidir.
    - Yemek siparişleri öğle ve akşam saatlerinde, taksi kullanımı ise sabah ve iş çıkışı saatlerinde güçlenir.
    - Pazarlar davranışlarına göre farklı profillere ayrılır: olgun yüksek hacimli pazarlar, yoğun Asya pazarları, Singapur gibi yüksek potansiyelli ayrışan pazarlar ve daha düşük talep/arz profilli pazarlar.

=== "Pipeline"

    Analiz; günlük pazar-kategori özellikleri, hava durumu seedleri, servis arzı metrikleri ve zaman bazlı işlem sinyallerini birleştirir. Python notebookları talep modellemesi ve pazar kümelenmesi için kullanılmıştır.
