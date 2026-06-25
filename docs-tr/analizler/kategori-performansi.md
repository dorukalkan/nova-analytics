---
icon: lucide/chart-bar
title: Kategori Performansı
description: Kategori bazlı gelir, risk, kalite, tekrar davranışı ve büyüme fırsatı dashboardu
author: Yasemen Nur Salım Dündar
---

# Kategori Performansı

![Tableau Kategori Performansı Dashboard'u](../assets/4_category.png)

=== "İçgörüler"

    Kategori performansı, ölçek ve güvenilirlik arasındaki denge hikayesidir. E-Commerce en büyük değer havuzudur, ancak en zayıf tamamlanma profiline de sahiptir. Digital Wallet çok daha küçüktür, fakat en güçlü operasyon kalitesini gösterir.

    !!! abstract "Ana çıkarım"

        Nova her kategoriyi eşit büyüme adayı olarak ele almamalıdır. En büyük fırsat, güvenilirlik kaybının pahalı olduğu yüksek GMV kategorilerini korumak ve daha güçlü kategorileri operasyonel benchmark olarak kullanmaktır.

    ## Temel Bulgular

    | Bulgu | Metrik | Yorum |
    | --- | --- | --- |
    | E-Commerce değer çıpası | **$1.11B GMV**, **%41.9 GMV payı** | Kategori platform değerinin en büyük bölümünü taşır |
    | E-Commerce aynı zamanda en zayıf tamamlanma profiline sahip | **%86.5 tamamlanma**, yaklaşık **%15.0 tamamlanmamış tutar oranı** | Buradaki güvenilirlik iyileştirmeleri en yüksek finansal kaldıraç etkisine sahip |
    | Food Delivery kullanım motoru | **14.86M işlem**, **%93.6 tamamlanma** | En çok etkileşimi üretir ve operasyonel olarak en büyük GMV kategorisinden daha iyi performans gösterir |
    | Grocery ikinci en büyük değer havuzu | **$520.8M GMV**, **%19.6 GMV payı**, **%91.5 tamamlanma** | Yeterince büyük bir kategori, ancak servis-risk yoğunlaşması için izlenmeli |
    | Ride Hailing stabilizasyona ihtiyaç duyuyor | **$312.2M GMV**, **%88.0 tamamlanma**, yaklaşık **%11.9 tamamlanmamış tutar oranı** | Kategori anlamlı ölçeğe sahip, ancak güvenilirliği daha zayıf |
    | Digital Wallet güvenilirlik benchmark'ı | **%96.6 tamamlanma**, **$279.6M GMV** | Daha küçük, fakat en güçlü uygulama kalitesini gösteriyor |

    ## İş İçgörüleri

    Kategori portföyü yalnızca GMV sıralaması değildir. E-Commerce en fazla ilgiyi hak eder; çünkü en büyük değer tabanını en görünür güvenilirlik kaybıyla birleştirir. Tamamlanma, hata veya refund davranışındaki küçük iyileştirmeler bile diğer kategorilerden daha büyük bir dolar tabanını etkiler.

    Food Delivery ve Grocery farklı bir hikaye anlatır. Food Delivery en yüksek etkileşim hacmine sahiptir; bu da onu günlük engagement ve operasyonel kapasite planlaması için önemli kılar. Grocery büyük bir değer havuzudur ve tamamlanma oranı makuldür; ancak dashboarddaki servis-risk dağılımı agresif ölçeklemeden önce izlenmesi gerektiğini gösterir.

    Dashboard ayrıca **3,067 kritik servis**, **4.4 ortalama rating** ve **%6.4 repeat user rate** gösterir. Bu, kategori performansının kategori seviyesinin altında yönetilmesi gerektiği anlamına gelir: servis sağlığı, servis yoğunlaşması ve risk segmenti karışımı büyümenin kalıcı olup olmadığını belirler.

    !!! success "Öneri"

        E-Commerce ve Ride Hailing'de güvenilirlik çalışmalarına öncelik verin, Digital Wallet'ı kalite benchmark'ı olarak kullanın ve yüksek tamamlanmama riski olan kategorilere büyüme yatırımı yapmadan önce kritik veya izleme gerektiren servisleri inceleyin.

=== "Yöntem"

    Bu analiz dbt service-health ve category-health modelleriyle oluşturulmuştur. Tahmine dayalı modelleme kullanmaz.

    ## dbt Model Akışı

    | Katman | Modeller | Amaç |
    | --- | --- | --- |
    | Staging | `stg_interactions`, `stg_services`, `stg_markets` | Düzeltilmiş işlem, servis ve pazar verisini standartlaştırır |
    | Intermediate | `int_services_enriched`, `int_service_interactions`, `int_service_health`, `int_service_risk`, `int_category_health` | Servisleri etkileşimlerle birleştirir, servis performansını agregeler, servis riskini sınıflandırır ve kategori sağlığını yukarı taşır |
    | Mart | `mart_category_performance`, `mart_category_market_performance`, `mart_marketplace_service` | Tableau hazır kategori, market-category ve servis seviyesi raporlama tabloları sağlar |

    ## Risk Mantığı

    Servis riski operasyonel sinyallerden atanır:

    | Sinyal | Rol |
    | --- | --- |
    | Success rate | Tamamlanan etkileşim güvenilirliğini ölçer |
    | Failure rate | Yüksek hata davranışı olan servisleri işaretler |
    | Refund rate | Gelir ve kalite kaçağını yakalar |
    | Rating | Müşteri taraflı servis kalitesi bağlamı ekler |

    Kategori dashboardu daha sonra bu servis seviyesi sinyalleri kategori seviyesi risk ve büyüme görünümlerine taşır.

    !!! tip "Neden önemli"

        Dashboard yalnızca ham kategori toplamlarını görselleştirmez. Servis seviyesi sağlık modeli üzerine kuruludur; bu da kategori performansının hem ölçeği hem de operasyonel kaliteyi yansıtmasını sağlar.
