---
icon: lucide/arrows-up-from-line
title: Staging Modelleri
description: Nova analitiği için temiz kaynak arayüzleri
---

# Staging Modelleri

Staging modelleri ham veya düzeltilmiş kaynak veriler ile analiz pipeline'ı arasındaki temiz arayüzdür. Alan adlarını standartlaştırır, kaynak grain'ini korur ve temel doğrulama kurallarını uygular.

Bu katmanın değeri basittir: analiz ve dashboard sorguları her seferinde ham alanları temizlemek zorunda kalmaz. İş mantığı daha sonra intermediate ve mart katmanlarında kurulur.

| Kaynak alanı | Rol |
| --- | --- |
| Etkileşimler | İşlem, kategori, kullanıcı ve servis ilişkilerini standartlaştırır. |
| Kullanıcılar | Müşteri profili ve segment analizleri için temiz kullanıcı alanları üretir. |
| Servisler | Kategori, servis kalitesi ve hizmet arzı analizlerini destekler. |
| Pazarlar | Şehir pazarı, ülke ve bölge bilgisini standartlaştırır. |
| Dış kaynaklar | Hava durumu, ülke metadatası ve makro göstergeleri pipeline'a bağlar. |
