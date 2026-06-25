---
icon: lucide/repeat
title: RFM Analizi
description: Recency, frequency ve monetary müşteri segmentasyonu dashboardu
author: Merve Kaymaz
---

# RFM Analizi

![Tableau RFM Analizi Dashboard'u](../assets/7_rfm_analysis.jpeg)

=== "İçgörüler"

    RFM Analizi, işlem geçmişini aksiyon odaklı bir müşteri portföyüne dönüştürür. Ana hikaye her segmentin aynı şekilde ele alınması gerektiği değildir: Champions ve Loyal Customers değerin çoğunu taşırken, Potential Loyalists en büyük geliştirme havuzudur.

    !!! abstract "Ana çıkarım"

        Nova'nın müşteri stratejisi önce en yüksek değerli segmentleri korumalı, ardından en büyük orta potansiyelli segmenti daha sık ve daha yüksek değerli davranışa dönüştürmelidir.

    ## Temel Bulgular

    | Bulgu | Metrik | Yorum |
    | --- | --- | --- |
    | Champions en yüksek değerli segment | Yaklaşık **242K müşteri**, **$1.34B** toplam harcama | Görece küçük bir grup en büyük değer havuzunu taşır |
    | Champions müşteri başına da en çok harcıyor | Yaklaşık **$5.55K** ortalama harcama | Churn veya servis kalitesi sorunlarından korunması gereken segment budur |
    | Loyal Customers ikinci değer havuzu | Yaklaşık **359K müşteri**, **$822.57M** toplam harcama | Zaten engaged durumdalar ve güçlendirilmeleri gerekir |
    | Potential Loyalists en büyük segment | Yaklaşık **481K müşteri**, müşterilerin **%28.18'i** | En büyük dönüşüm fırsatı budur |
    | Potential Loyalists mevcut değeri daha düşük | Yaklaşık **$197.92M toplam harcama ve $412** ortalama harcama | Segment yalnızca retention mesajına değil, frequency ve monetary growth'a ihtiyaç duyar |
    | At Risk müşteriler hala geri kazanılabilir değer içeriyor | Yaklaşık **222K müşteri**, **$184.23M** toplam harcama | Geniş Lost Customer kampanyalarından önce reactivation burada odaklanmalı |

    ## İş İçgörüleri

    RFM segmentasyonu müşteri büyüklüğü ile müşteri değerini ayırır. Champions en büyük grup değildir, ancak en yüksek toplam harcamayı ve en yüksek ortalama harcamayı üretir. Bu segmentte kalite veya engagement kaybı, çok daha büyük ama düşük değerli bir grubun kaybından daha pahalı olur.

    Potential Loyalists stratejik geliştirme havuzudur. En büyük segmenttir, ancak ortalama harcaması Champions ve Loyal Customers'ın çok altındadır. Fırsat, hedefli lifecycle teklifleri ve kategori önerileriyle onları orta düzey engagement'dan tekrar eden, daha yüksek frekanslı davranışa taşımaktır.

    Reactivation seçici olmalıdır. At Risk müşteriler anlamlı geri kazanılabilir değer taşırken, Lost Customers sayıca daha büyük ama değer olarak çok daha düşüktür. Big Spenders müşterilerin yalnızca yaklaşık **%0.46'sı** olduğu için kitlesel kampanyalardan çok high-touch uygulamalarına daha uygundur.

    !!! success "Öneri"

        Champions'ı koruyun, Loyal Customers'ı güçlendirin, Potential Loyalists için dönüşüm programları kurun ve Lost Customer reactivation'a yoğun yatırım yapmadan önce At Risk geri kazanımına öncelik verin.

=== "Yöntem"

    Bu sayfa analiz için kullanılan dbt modellerini içerir.

    ## dbt Model Akışı

    | Model | Grain | Rol |
    | --- | --- | --- |
    | `int_customer_metrics` | customer | Transaction count, total spend, average order value, first and last order date, customer lifetime days, category count ve services used hesaplar |
    | `int_rfm_features` | customer | Recency, frequency ve monetary alanlarını türetir |
    | `int_rfm_scores` | customer | Recency, frequency ve monetary value için 1-5 skorları atar |
    | `mart_customer_segments` | customer | Skorları iş dostu segment etiketlerine eşler |

    ## Segment Mantığı

    | Segment | Kural yorumu |
    | --- | --- |
    | Champions | Yakın zamanda aktif, sık işlem yapan ve yüksek değerli müşteriler |
    | Loyal Customers | Kabul edilebilir recency ile güçlü frequency |
    | New Customers | Daha düşük frequency'ye sahip yeni müşteriler |
    | Big Spenders | Daha düşük frequency ile yüksek monetary value |
    | At Risk | Daha zayıf recency'ye sahip, geçmişte aktif müşteriler |
    | Lost Customers | En zayıf recency'ye sahip müşteriler |
    | Potential Loyalists | Diğer açık gruplara girmeyen müşteriler |

    !!! tip "Neden önemli"

        RFM, ham işlem geçmişini marketing, retention ve müşteri stratejisi ekipleri tarafından kullanılabilecek basit bir önceliklendirme çerçevesine dönüştürür.
