---
icon: lucide/shield-alert
title: Müşteri Tekrarı ve Risk
description: Müşteri sadakati, tekrar davranışı ve işlem riski dashboardu
author: Yasemen Nur Salım Dündar
---

# Müşteri Tekrarı ve Risk

![Tableau Müşteri Tekrarı ve Risk Dashboard'u](../assets/5_customer_risk.png)

=== "İçgörüler"

    !!! note "İş özeti"

        Tekrar davranışı müşteri değerini gösterirken, anormal işlem örüntüleri operasyonel inceleme ihtiyacını gösterir. Bu analiz iki bakışı aynı dashboardta birleştirir.

    ## İş İçgörüleri

    - Tekrar eden müşteriler retention ve büyüme açısından daha anlamlı hedeflerdir.
    - Yüksek riskli veya olağandışı işlem kümeleri otomatik karar yerine inceleme kuyruğu için önceliklendirme sinyali olarak kullanılmalıdır.
    - Risk analitiği, müşteri değerini cezalandırmadan şüpheli işlem örüntülerini görünür kılmalıdır.

=== "Pipeline"

    dbt modelleri tekrar davranışı, işlem hacmi ve müşteri düzeyi risk özelliklerini üretir. Fraud analytics tarafında Python/Jupyter içinde Isolation Forest ile denetimsiz anomali skorlaması yapılmıştır.
