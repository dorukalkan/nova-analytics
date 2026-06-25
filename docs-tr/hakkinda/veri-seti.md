---
icon: lucide/database
title: Veri Seti
description: Nova analitik projesinin kaynak veri seti ve düzeltme yaklaşımı
---

# Veri Seti

Bu proje, global bir super-app için işlemleri, kullanıcıları, servisleri ve faaliyet pazarlarını temsil eden sentetik bir pazaryeri veri seti olan public [Nova 50M Transactions Super-App dataset](https://www.kaggle.com/datasets/adityathakekar/nova-50m-transactions-super-app) ile başlar.

## Ne İçeriyor?

Kaynak veri dört çekirdek varlık içerir:

| Varlık | Neyi temsil eder | Örnek alanlar |
| --- | --- | --- |
| Interactions | İşlem seviyesi pazaryeri aktivitesi | User, service, category, amount, status, timestamp, platform, referral source, location |
| Users | Müşteri profili özellikleri | Membership tier, device, acquisition source, market |
| Services | Servis ve kategori metadatası | Category, rating, marketplace availability |
| Markets | Şehir seviyesi faaliyet pazarları | Market name, region, latitude, longitude |

## Nasıl Kullandık?

Orijinal veri setini başlangıç noktası olarak ele aldık, ardından final analitik katmanı kurmadan önce veri setini gerçekçilik için yeniden ürettik.

Yeniden üretim adımı proje ölçeğini ve çekirdek şemayı korudu; ancak daha gerçekçi iş davranışları ekledi: pazar seviyesi sezonluk değişim, kategoriye özel talep ve sepet büyüklükleri, hava durumu duyarlılığı, servis arzı etkileri, müşteri yaşam döngüsü çeşitliliği ve fraud benzeri işlem örüntüleri.

Bu projedeki dashboardlar ve dbt modelleri, ham Kaggle dosyalarını doğrudan değil, yeniden üretilmiş veri setini kullanır.
