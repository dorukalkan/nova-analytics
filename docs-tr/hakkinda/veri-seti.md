---
icon: lucide/database
title: Veri Seti
description: Nova analitik projesinin kaynak veri seti ve düzeltme yaklaşımı
---

# Veri Seti

Proje, public [Nova 50M Transactions Super-App dataset](https://www.kaggle.com/datasets/adityathakekar/nova-50m-transactions-super-app) üzerine kuruludur. Veri seti global bir super-app için işlemleri, kullanıcıları, servisleri ve faaliyet pazarlarını temsil eden sentetik bir pazaryeri verisidir.

## Ne İçeriyor?

| Alan | Açıklama |
| --- | --- |
| Etkileşimler | İşlem zamanı, kullanıcı, servis, kategori, pazar ve tutar bilgileri. |
| Kullanıcılar | Müşteri profili ve segment analizleri için kullanıcı özellikleri. |
| Servisler | Servis kategorisi, kalite ve hizmet arzı analizleri için alanlar. |
| Pazarlar | Şehir pazarı, ülke, bölge ve coğrafi kapsam. |
| Dış zenginleştirme | Hava durumu, ülke metadatası ve makroekonomik göstergeler. |

## Neden Yeniden Ürettik?

Veri setini daha gerçekçi analiz yapılabilecek hale getirmek için yeniden ürettik. Amaç; sezonluk davranış, pazar farklılıkları, müşteri yaşam döngüsü, kategori davranışı, hava durumu etkisi ve fraud benzeri örüntüleri daha tutarlı hale getirmekti.
