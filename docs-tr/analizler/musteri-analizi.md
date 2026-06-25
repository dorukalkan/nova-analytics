---
icon: lucide/user-round-check
title: Müşteri Analizi
description: Müşteri segmentasyonu ve yaşam döngüsü davranışı dashboardu
author: Merve Kaymaz
---

# Müşteri Analizi

![Tableau Müşteri Analizi Dashboard'u](../assets/6_customer_analysis.jpeg)

=== "İçgörüler"

    Müşteri Analizi, Nova'daki müşteri değerinin yüksek ölçüde yoğunlaştığını gösterir. Premium üyeler kullanıcı tabanının azınlığıdır, ancak completed revenue'nun çoğunu üretir. High Value lifecycle müşterileri de aynı örüntüyü gösterir: sayıca daha küçük, ekonomik etkisi çok daha büyük.

    !!! abstract "Ana çıkarım"

        Nova müşteri büyümesini yalnızca kullanıcı sayısı etrafında değil, değer yoğunlaşması etrafında yönetmelidir. Premium dönüşüm, high-value retention ve kanal kalitesi geniş edinim hacminden daha önemlidir.

    ## Temel Bulgular

    | Bulgu | Metrik | Yorum |
    | --- | --- | --- |
    | Premium üyeler azınlık | Müşterilerin **%25.28'i** Gold veya Platinum | Premium taban hala büyümeye yeterince açık |
    | Premium üyeler completed revenue'nun çoğunu taşıyor | **$2.36B** completed revenue'nun yaklaşık **$1.56B** bölümü | Membership tier müşteri değeriyle güçlü şekilde ilişkili |
    | Platinum müşteriler en yüksek değerli tier | Müşteri başına **$5,397** ortalama completed revenue | Platinum davranışı en net high-value benchmark |
    | Gold müşteriler de Standard'dan yüksek performans gösteriyor | Müşteri başına **$2,374 vs $534** ortalama completed revenue | Standard müşterileri upgrade etmek müşteri ekonomisini anlamlı şekilde iyileştirebilir |
    | Organic Search en büyük edinim kanalı | Müşterilerin **%32.14'ü** ve **$756.64M** completed revenue | Organic discovery hem en büyük kullanıcı kaynağı hem de en büyük gelir kanalı |
    | High Value müşteriler lifecycle revenue'yu domine ediyor | **199K** müşteri **$1.44B** completed revenue üretiyor | En değerli lifecycle grubu en büyük müşteri grubundan çok daha küçük |

    ## İş İçgörüleri

    Membership tier bu sayfadaki en net değer sinyalidir. Standard müşteriler tabanın çoğunu oluşturur, ancak Platinum ve Gold müşteriler müşteri başına çok daha fazla değer üretir. Bu, ana müşteri fırsatının yalnızca daha fazla kullanıcı edinmek değil, doğru kullanıcıları daha yüksek değerli davranışa taşımak olduğunu gösterir.

    Edinim kalitesi de önemlidir. Organic Search hem en büyük müşteri sayısını hem de en büyük completed revenue'yu getirirken, Push Notification hacim olarak daha küçüktür ama edinim kaynakları arasında müşteri başına en yüksek ortalama completed revenue'ya sahiptir. Kanal stratejisi ölçek ile verimliliği ayırmalıdır.

    Lifecycle segmentasyonu retention önceliğini netleştirir. Retained müşteriler yaklaşık **1.09M** kullanıcı ve **$821.71M** completed revenue ile en büyük gruptur; ancak High Value müşteriler çok daha küçük bir tabandan daha fazla gelir üretir. Inactive müşteriler yaklaşık **300K** ile sayıca büyüktür, fakat neredeyse hiç mevcut değer üretmez.

    !!! success "Öneri"

        Önce premium dönüşüm ve High Value retention'a öncelik verin, Organic Search'ü ana edinim motoru olarak güçlü tutun ve Push Notification gibi düşük hacimli kanalları geniş erişim yerine hedefli high-value engagement için kullanın.

=== "Yöntem"

    Bu sayfa analiz için kullanılan dbt modellerini içerir.

    ## dbt Model Akışı

    | Katman | Modeller | Amaç |
    | --- | --- | --- |
    | Staging | `stg_users`, `stg_interactions` | Düzeltilmiş kullanıcı ve işlem verisini standartlaştırır |
    | Mart | `mart_customer_overview` | Profil alanları ve işlem metrikleriyle müşteri başına tek satır üretir |

    ## Customer Mart Alanları

    `mart_customer_overview` şunları birleştirir:

    | Alan grubu | Örnekler |
    | --- | --- |
    | Profil | membership tier, primary device, market, acquisition source, user segment, lifecycle segment, join date |
    | Aktivite | transaction count, completed transaction count, first order date, last order date |
    | Değer | total revenue, average order value |
    | Recency | customer age ve days since last order |

    !!! tip "Neden önemli"

        Tableau sayfası müşteri seviyesi kayıtlardan kurulur; bu nedenle membership, acquisition, lifecycle ve revenue dashboard içinde ham işlemleri yeniden agreglemeden karşılaştırılabilir.
