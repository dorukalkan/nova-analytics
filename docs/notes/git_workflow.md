---
icon: lucide/notebook
title: Git & dbt workflow
description: Git & dbt workflow
---

## Git + dbt Çalışma Akışı

Bu sayfa, kendi branch'inde güvenli şekilde çalışmak, dbt modellerini kontrol etmek ve değişiklikleri Pull Request ile `main` branch'ine eklemek için hazırlanmıştır.

Temel mantık:

```text
main = projenin temiz / çalışan hali
feature branch = kendi işin için açtığın ayrı dal
PR = yaptığın işi main'e eklemeden önce kontrol etme ve birleştirme adımı
```

!!! warning "main branch'te direkt çalışma"

    `main` branch projenin ortak ve temiz hali gibi düşünülmeli. Yeni bir iş yaparken önce `main`'i güncelle, sonra ayrı bir branch aç.

!!! note "Her yeni iş için kısa akış"

    `main` -> yeni branch -> değişiklik -> dbt build -> commit -> push -> PR

## 1. main branch'i güncelle

Yeni işe başlamadan önce `main` branch'inin güncel olduğundan emin ol.

```bash
git checkout main
git pull
```

Bu komutlardan sonra bilgisayarındaki `main`, GitHub'daki güncel `main` ile aynı hale gelir.

## 2. Yeni branch aç

Her yeni iş için ayrı bir branch aç.

```bash
git checkout -b my-new-branch
```

Branch adını yaptığın işe göre kısa ve anlaşılır seçmek iyi olur.

Örnek branch adları:

```bash
git checkout -b add-stg-users
git checkout -b add-service-kpi-mart
git checkout -b fix-source-tests
git checkout -b add-retention-models
```

??? info "Branch nedir?"

    Branch, `main` branch'ini bozmadan kendi değişikliklerini yapabildiğin ayrı çalışma alanıdır.

## 3. Değişikliklerini yap ve kontrol et

Model, schema, test veya doküman değişikliklerini yaptıktan sonra ilk bakılacak komut:

```bash
git status
```

Bu komut sana hangi branch'te olduğunu, hangi dosyaların değiştiğini ve Git'in senden ne beklediğini gösterir.

!!! note

    Bir şey karışırsa önce `git status` çalıştır. Git çoğu zaman bir sonraki adımı burada açıklar.

## 4. dbt proje klasörüne gir ve modeli test et

Bu repoda dbt projesi `nova` klasörünün içinde.

```bash
cd nova
```

Sonra kendi modelini ve ona bağlı önceki modelleri çalıştır:

```bash
uv run dbt build --select +my_model
```

Burada `my_model` yerine kendi model adını yazmalısın.

Örnek:

```bash
uv run dbt build --select +stg_users
```

Bu komutun mantığı:

- `dbt build`: Modeli çalıştırır ve testleri de kontrol eder.
- `--select +my_model`: Seçtiğin modelle birlikte o modelin ihtiyaç duyduğu önceki modelleri de dahil eder.
- Baştaki `+`: "Bu modelin bağlı olduğu upstream modelleri de çalıştır" anlamına gelir.

!!! note "Emin değilsen daha geniş kontrol yap"

    Eğer staging veya source tarafında değişiklik yaptıysan ve hangi modellerin etkilendiğinden emin değilsen, tüm projeyi kontrol etmek daha güvenlidir:

    ```bash
    uv run dbt build
    ```

## 5. Değişiklikleri commit et

dbt build başarılıysa değişikliklerini Git'e ekle.

```bash
git add .
```

İstersen sadece belirli bir dosyayı da ekleyebilirsin:

```bash
git add nova/models/staging/stg_users.sql
```

Sonra kısa ve açıklayıcı bir commit mesajı yaz:

```bash
git commit -m "Add staging model for users"
```

İyi commit mesajı örnekleri:

```bash
git commit -m "Add service KPI mart"
git commit -m "Add staging model for interactions"
git commit -m "Fix source tests"
```

Çok genel mesajlardan kaçın:

```bash
git commit -m "update"
git commit -m "changes"
git commit -m "fix"
```

## 6. PR açmadan önce branch'i güncel tut

Sen çalışırken başka biri `main` branch'ine yeni değişiklikler eklemiş olabilir. PR açmadan önce kendi branch'ini güncel `main` ile birleştirmek iyi olur.

Önce GitHub'daki son durumu bilgisayarına çek:

```bash
git fetch origin
```

Sonra güncel `main` branch'ini kendi aktif branch'inle birleştir:

```bash
git merge origin/main
```

Eğer conflict çıkarsa Git hangi dosyalarda çakışma olduğunu söyler. O dosyaları düzenleyip conflict'i çözdükten sonra:

```bash
git add .
git commit
```

Conflict çözdükten sonra dbt build'i tekrar çalıştırmak iyi olur:

```bash
cd nova
uv run dbt build --select +my_model
```

??? info "`origin` ve `-u` ne demek?"

    `origin`, GitHub'daki remote repo adıdır. `-u`, local branch ile GitHub'daki branch'i birbirine bağlar. İlk push'tan sonra aynı branch'te sadece `git push` yazmak yeterli olur.

## 7. Branch'i GitHub'a gönder

Branch'i ilk kez GitHub'a gönderiyorsan:

```bash
git push -u origin my-new-branch
```

Aynı branch'te daha sonra tekrar push atacaksan:

```bash
git push
```

## 8. GitHub'da Pull Request aç

GitHub'da repo'ya gir ve kendi branch'in için Pull Request aç.

```text
base: main
compare: senin-branch-adin
```

Örnek:

```text
base: main
compare: add-service-kpi-mart
```

PR açıklamasında kısaca şunları yazmak iyi olur:

```text
Ne yaptım?
- Yeni mart modeli ekledim.
- İlgili schema testlerini ekledim.
- dbt build ile kontrol ettim.

Nasıl test ettim?
- uv run dbt build --select +mart_service_kpis
```

PR, yaptığın işi `main` branch'ine eklemeden önce kontrol etmek için kullanılır.

## 9. PR merge edildikten sonra local main'i güncelle

PR merge edildikten sonra kendi bilgisayarındaki `main` branch hâlâ eski olabilir.

Önce `main` branch'e geç:

```bash
git checkout main
```

Sonra GitHub'daki güncel `main` branch'i çek:

```bash
git pull
```

Yeni bir işe başlayacaksan yine yeni branch aç:

```bash
git checkout -b next-branch
```

## Kısa Özet

Günlük çalışma akışı genelde şöyle olur:

```bash
# main branch'e geç (üzerinde çalıştığın branch'le işin bittiyse)
git checkout main

# main'de herhangi bir değişiklik varsa lokal repona pull et
git pull

# üzerinde çalışmak için yeni branch oluştur
git checkout -b my-new-branch

# kod değişikliklerini yap

# kendi değişikliklerini + main'deki değişikliklerin durumunu kontrol et
git status

# yaptığın & kaydettiğin dosyalardaki tüm değişiklikleri ekle
git add .

# alternatif: tek bir dosyayı eklemek için örnek
git add notebooks/my_notebook.ipynb

# yaptığın değişikliklere açıklayıcı ama kısa commit mesajı ekle
git commit -m "fix revenue_model grain issue"

# kendi değişikliklerini pushlamadan önce main'dekileri al
git fetch origin

# tüm değişikliklerle beraber main'e mergele (sonra github'dan pull request yap)
git merge origin/main

# dbt proje klasörüne geç
cd nova

# modelini build et ve bigquery'de kontrol et
uv run dbt build --select +my_model

# branch'ini remote repoya pushla (branch'inde ilk push ise -u kullanılır, sonraki pushlarda gerek yok)
git push -u origin my-new-branch
```

Sonra GitHub'da PR açılır.

PR merge edildikten sonra:

```bash
# tekrar main'e geç (kendi değişikliklerin silinmiş gibi gözükecek, panik yapma)
git checkout main

# branch'inden remote repoya attığın değişiklikleri main'ine geri çek
# (yaptığın değişiklikler geri gelecek)
git pull

# yeni branch
git checkout -b next-branch
```

## Önemli Kurallar

### 1. Doğrudan main branch'te çalışmamaya çalış

`main` branch projenin temiz ve çalışan hali olmalı. Yeni işler için ayrı branch açmak daha güvenli.

Yanlışlıkla `main` branch'teysen:

```bash
git branch
```

Aktif branch'in yanında `*` işareti olur.

### 2. PR açmadan önce dbt build çalıştır

PR açmadan önce en azından kendi modelini ve bağlı modelleri test et:

```bash
uv run dbt build --select +my_model
```

Bu, bozuk SQL, eksik kaynak veya başarısız test gibi hataları önceden yakalamamızı sağlar.

### 3. Branch'i güncel tut

PR açmadan önce:

```bash
git fetch origin
git merge origin/main
```

yapmak iyi bir alışkanlıktır.

### 4. Commit mesajlarını açıklayıcı yaz

Commit mesajı kısa olsun ama ne yaptığını anlatsın.

```bash
git commit -m "Add staging model for users"
git commit -m "Add tests for transaction source"
git commit -m "Create service KPI mart"
```

### 5. Hata çıkarsa önce git status çalıştır

Bir şey karışırsa ilk bakılacak komut:

```bash
git status
```

Bu komut sana hangi branch'te olduğunu, hangi dosyaların değiştiğini ve Git'in senden ne beklediğini gösterir.
