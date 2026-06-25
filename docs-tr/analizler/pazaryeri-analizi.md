---
icon: lucide/map
title: Pazaryeri Analizi
description: Pazar fırsatı, bölgesel performans ve büyüme önceliklendirmesi dashboardu
author: Doruk Alkan
---

# Pazaryeri Analizi ve Büyüme Fırsatları

![Tableau Pazaryeri Analizi Dashboard'u](../assets/2_marketplace_analysis.png)

=== "İçgörüler"

    Nova'nın pazaryeri ayak izi **4 kıta**, **8 bölge** ve **16 şehir pazarına** yayılır. Kapsam globaldir; ancak kullanım oldukça yoğunlaşmıştır: **Asya işlemlerin %74.65'ini** ve GMV'nin yaklaşık **%69.6'sını** oluşturur.

    En güçlü işlem pazarları Güney ve Güneydoğu Asya'da kümelenir. **Jakarta ilk sıradadır**; onu **Mumbai**, **Manila**, **Bangalore** ve **Singapore** takip eder. İstanbul **7. sıradadır**, Sydney ise işlem sayısına göre en küçük pazardır.

    !!! abstract "Ana çıkarım"

        Nova'nın büyüme hikayesi pazar odaklıdır. Güney ve Güneydoğu Asya talep tabanını taşırken, Singapore en net stratejik fırsat pazarı olarak öne çıkar.

    ## Temel Bulgular

    | Bulgu | Metrik | Yorum |
    | --- | --- | --- |
    | Asya pazaryeri aktivitesini domine ediyor | **İşlemlerin %74.65'i**, GMV'nin yaklaşık **%69.6'sı** | Nova'nın temel operasyonel gücü Asya pazarlarında yoğunlaşıyor |
    | Hindistan en büyük ülke ayak izi | **İşlemlerin %16.14'ü** | Mumbai ve Bangalore üzerinden Hindistan en büyük ülke düzeyi talep tabanı |
    | En büyük pazarlar Güney/Güneydoğu Asya'da | Jakarta, Mumbai, Manila, Bangalore, Singapore | En yüksek hacimli pazarlar yakın büyüme bölgelerinde yoğunlaşıyor |
    | Singapore fırsat skorunda birinci | Dashboard'daki en yüksek fırsat skoru | Güçlü makro/dijital bağlam Singapore'u stratejik büyüme adayı yapıyor |
    | Sydney en küçük pazar | 16 pazar içinde en düşük işlem sayısı | Düşük hacimli pazarlar agresif büyüme playbook'u uygulanmadan önce teşhis edilmeli |

    ## İş İçgörüleri

    Nova tek bir global büyüme playbook'u kullanmamalıdır. Jakarta, Mumbai, Manila ve Bangalore gibi yüksek hacimli pazarlar arz koruması ve operasyonel tutarlılık gerektirir. Singapore ise güçlü fırsat skoru ile premium ve yüksek dijital pazar bağlamını birleştirdiği için ayrı stratejik ilgi hak eder.

    Daha geniş izleme pazarlarında öncelik teşhistir: yatırım artırmadan önce büyümenin talep, servis arzı, güvenilirlik veya yerel pazar bağlamı tarafından mı sınırlı olduğunu anlamak gerekir.

    !!! success "Öneri"

        En net büyüme hikayesi olarak Güneydoğu Asya ve Singapore'a öncelik verin; yüksek hacimli, olgun ve düşük arzlı pazarlar için pazara özel playbook'lar kullanın.

=== "Yöntem"

    Bu analiz, dış coğrafya, hava durumu ve makroekonomik bağlamla zenginleştirilmiş Nova işlem verisi üzerine kuruludur.

    ## Veri Zenginleştirme

    | Kaynak | Analizdeki rolü | Seed çıktısı |
    | --- | --- | --- |
    | Gözden geçirilmiş pazar-ülke eşlemesi | Nova şehir pazarlarını ülke tanımlayıcılarına bağlar | `market_country_lookup.csv` |
    | REST Countries | Bölge, alt bölge, para birimi, başkent ve zaman dilimi gibi ülke metadatası ekler | `ext_country_metadata.csv` |
    | World Bank | Nüfus, kişi başı GDP, kentleşme, internet kullanımı ve mobil abonelik gibi makro göstergeler ekler | `ext_world_bank_indicators.csv` |
    | Open-Meteo | Coğrafya analizinin başka bölümlerinde kullanılan günlük hava durumu bağlamını ekler | `ext_weather_daily.csv` |

    ## dbt Model Akışı

    | Katman | Modeller | Amaç |
    | --- | --- | --- |
    | Staging | `stg_geo_market_country_lookup`, `stg_geo_country_metadata`, `stg_geo_world_bank_indicators`, `stg_markets`, `stg_interactions` | Ham ve seed girdilerini standartlaştırır |
    | Intermediate | `int_geo_country_macro_pivot`, `int_geo_market_context`, `int_geo_market_day_metrics`, `int_geo_service_supply_by_market_category` | Ülke başına tek satır, pazar bağlamı, market-day performansı ve servis arzı özellikleri oluşturur |
    | Mart | `mart_geo_market_opportunity` | Pazar fırsat skorunu, sırasını ve fırsat segmentini hesaplar |

    ## Fırsat Skoru

    Fırsat martı mevcut performansı, makro potansiyeli, servis arzını ve adoption sinyallerini 0-100 arası bir skorda birleştirir. Skor bir tahmin değildir; 16 Nova pazarını karşılaştırmak için yapılandırılmış bir önceliklendirme metriğidir.

    !!! warning "Yorum"

        Fırsat skoru sıralama ve tartışma için kullanışlıdır, ancak karar destek metriği olarak ele alınmalıdır. Pazara özel iş incelemesinin yerini almaz.
