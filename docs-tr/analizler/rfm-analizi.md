---
icon: lucide/repeat
title: RFM Analizi
description: Recency, frequency ve monetary müşteri segmentasyonu dashboardu
author: Merve Kaymaz
---

# RFM Analizi

![Tableau RFM Analizi Dashboard'u](../assets/7_rfm_analysis.jpeg)

=== "İçgörüler"

    !!! note "İş özeti"

        RFM analizi müşterileri ne kadar yakın zamanda, ne sıklıkla ve ne kadar değerle işlem yaptıklarına göre sınıflandırır. Amaç retention ve yeniden aktivasyon önceliklerini netleştirmektir.

    ## İş İçgörüleri

    - Yakın zamanda aktif olan, sık işlem yapan ve yüksek harcama yapan müşteriler korunması gereken çekirdek gruptur.
    - Uzun süredir aktif olmayan ancak geçmiş değeri yüksek müşteriler geri kazanım kampanyaları için daha anlamlı hedeflerdir.
    - RFM sayfasında ayrı bir modelleme notebooku yoktur; segmentler dbt ile hazırlanıp Tableau'da iş yorumu için görselleştirilmiştir.

=== "Pipeline"

    RFM skoru müşteri işlem geçmişinden türetilir. dbt modelleri recency, frequency ve monetary ölçümlerini standardize eder; mart çıktısı Tableau'da segment dağılımı ve retention öncelikleri için kullanılır.
