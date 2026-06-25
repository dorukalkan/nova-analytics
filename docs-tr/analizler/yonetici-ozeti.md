---
icon: lucide/layout-dashboard
title: Yönetici Özeti
description: Nova pazaryeri performansı ve büyüme sinyalleri için yönetici dashboard özeti
author: Doruk Alkan
---

# Yönetici Özeti

![Tableau Yönetici Özeti Dashboard'u](../assets/1_exec_summary.png)

=== "İçgörüler"

    Nova, yeniden üretilmiş 2024 veri setinde **50M etkileşim** üzerinden **$2.66B GMV** işledi. GMV, yani Gross Merchandise Value, platform üzerinden akan toplam işlem değerini temsil eder; bu tutar merchant geliri ve Nova komisyonu ayrıştırılmadan önceki toplam hacimdir.

    Yıl boyunca Nova, **50K servis** aracılığıyla **1.71M aktif kullanıcıya** hizmet verdi. Ana hikaye; geç yıl ivmesi, güçlü kategori yoğunlaşması ve anlamlı müşteri segmentasyonu sinyalleri olan ölçekli bir pazaryeridir.

    !!! abstract "Ana çıkarım"

        Nova halihazırda pazaryeri ölçeğinde çalışıyor. Bundan sonraki soru aktivite olup olmadığı değil; bu aktivitenin nerede yoğunlaştığı ve hangi kaldıraçların ölçeği daha kaliteli büyümeye dönüştürebileceğidir.

    ## Temel Bulgular

    | Bulgu | Metrik | Yorum |
    | --- | --- | --- |
    | Pazaryeri ölçeği | **$2.66B GMV**, **50M etkileşim**, **1.71M aktif kullanıcı**, **50K servis** | Nova, pazar, kategori, müşteri ve risk analizlerinin anlamlı olacağı ölçekte çalışıyor |
    | Yıl sonu büyümesi | **Aylık GMV Ocak'ta $171.7M'den Aralık'ta $327.5M'ye yükseldi** | Modellenmiş pazaryeri güçlü yıl sonu ivmesi gösteriyor |
    | Kategori yoğunlaşması | **E-Commerce yaklaşık $1.11B GMV ile lider** | E-Commerce en büyük değer sürücüsü ve yakın performans/risk takibi gerektiriyor |
    | Müşteri tabanı yapısı | **Potential Loyalists yaklaşık 481K müşteriyle en büyük segment** | En büyük müşteri havuzu henüz tam olgunlaşmamış; bu da upsell ve retention fırsatı yaratıyor |

    ## İş İçgörüleri

    Nova'nın 2024 performansı eşit dağılmıyor. E-Commerce en büyük GMV'yi taşıyor, müşteri segmentleri olgunluk açısından belirgin şekilde ayrışıyor ve aylık değer yıl boyunca artıyor. Bu nedenle geri kalan analizler gerekli: büyüme stratejisi **Nova'nın nerede faaliyet gösterdiğini**, **yerel talebi neyin etkilediğini**, **hangi kategorilerin operasyonel risk taşıdığını** ve **hangi müşteri gruplarının geliştirilebileceğini** hesaba katmalıdır.

    !!! success "Önerilen okuma"

        Büyümenin nereden gelebileceğini anlamak için pazaryeri ve talep etkenleri sayfalarıyla başlayın. Ardından bu büyümeyi nasıl koruyacağınızı belirlemek için kategori, müşteri ve risk sayfalarını kullanın.

=== "Yöntem"

    Yönetici Özeti, tek başına bir dashboard değil; tam bir analitik pipeline'ın final sunum katmanıdır.

    ## Pipeline Özeti

    | Aşama | Yapılan iş | Ana çıktılar |
    | --- | --- | --- |
    | Veri seti düzeltmesi | Sentetik Nova veri seti daha gerçekçi sezonluk davranış, pazar davranışı, müşteri yaşam döngüsü, kategori davranışı, hava durumu etkileri ve fraud benzeri sinyaller için yeniden üretildi | `scripts/generate_corrected_dataset.py`, `scripts/validate_corrected_dataset.py` |
    | Veri ambarına yükleme | Düzeltilmiş Nova etkileşimleri, kullanıcıları, servisleri ve pazarları BigQuery'ye yüklendi | `source('raw', ...)` tabloları |
    | dbt modelleme | Ham kaynaklar standartlaştırıldı, intermediate metrikler oluşturuldu ve analiz hazır martlar materialize edildi | `stg_*`, `int_*`, `mart_*` modelleri |
    | Notebook modelleme | Analizin gerektirdiği yerlerde tahmine dayalı veya denetimsiz modelleme yapıldı | talep regresyonu, pazar kümelenmesi, fraud anomali notebookları |
    | Görselleştirme | dbt martları ve notebook çıktılarından Tableau sayfaları yayınlandı | analiz bölümünde gösterilen dashboard ekran görüntüleri |

    ## Kalite Kapıları

    Dashboardlar yorumlanmadan önce pipeline doğrulama içerir:

    - düzeltilmiş veri seti validasyonu 50M satırı, anahtar kapsamını, tarih kapsamını, kategori/servis tutarlılığını, yaşam döngüsü çeşitliliğini, hava durumu duyarlılığını ve fraud benzeri davranış sinyallerini doğrular;
    - dbt schema testleri ana alanları, kabul edilen değerleri ve ilişkileri zorunlu kılar;
    - özel dbt testleri coğrafya grain'lerini, feature-mart kapsamını, market-day ve category-day toplamları arasındaki mutabakatı ve hava durumu tekilliğini kontrol eder.

    !!! success "Neden önemli"

        Yönetici dashboardu yalnızca final çıktıdır. Projenin değeri, dashboardu güvenilir yapan veri düzeltme, dönüşüm, test, modelleme ve yorumlama çalışmasından gelir.
