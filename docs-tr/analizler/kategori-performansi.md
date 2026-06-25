---
icon: lucide/chart-bar
title: Kategori Performansı
description: Kategori bazlı gelir, risk, kalite, tekrar davranışı ve büyüme fırsatı dashboardu
author: Yasemen Nur Salım Dündar
---

# Kategori Performansı

![Tableau Kategori Performansı Dashboard'u](../assets/4_category.png)

=== "İçgörüler"

    !!! note "İş özeti"

        Kategori büyümesi yalnızca GMV artışıyla değerlendirilmemelidir. Servis güvenilirliği, iptal/iade sinyalleri, müşteri tekrarı ve riskli işlem örüntüleri kategori sağlığını birlikte belirler.

    ## İş İçgörüleri

    - Yüksek hacimli kategoriler gelir fırsatı taşırken operasyonel aksaklıklara daha duyarlıdır.
    - Kategori performansı, hizmet kalitesi ve tekrar davranışıyla birlikte okunduğunda daha net öncelikler verir.
    - Büyüme önerileri kategori bazlı olmalıdır: güçlü kategorilerde kapasite korunmalı, riskli kategorilerde güvenilirlik ve işlem kalitesi iyileştirilmelidir.

=== "Pipeline"

    Bu sayfa kategori, servis, işlem ve müşteri davranışı sinyallerini birleştiren dbt modellerinden beslenir. Mart çıktıları Tableau'da kategori sağlığı ve büyüme önceliklerini göstermek için kullanılır.
