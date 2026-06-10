---
icon: lucide/notebook
title: Git & dbt workflow
description: Git & dbt workflow
---

## Git + dbt Çalışma Akışı

Bu akış, kendi branch’imizde çalışıp değişiklikleri güvenli şekilde GitHub’a göndermek, dbt modellerini test etmek ve sonra main branch’e merge etmek için kullanılabilir.

Temel mantık şu:

text main = projenin temiz / çalışan hali feature branch = kendi üzerinde çalıştığın ayrı dal PR = yaptığın işi main’e eklemeden önce kontrol etme ve birleştirme adımı 


### 1. Kendi branch’ini remote’a gönder

Önce yaptığın branch’i GitHub’a gönderiyoruz:

bash git push -u origin drk-add-marts 

Buradaki mantık:

- origin: GitHub’daki repo.
- drk-add-marts: Üzerinde çalıştığın branch adı.
- -u: Bu local branch ile GitHub’daki remote branch’i birbirine bağlar.

Bu komuttan sonra ileride aynı branch’te tekrar push atarken sadece şunu yazmak yeterli olur:

bash git push 


### 2. main branch’teki güncel değişiklikleri kendi branch’ine al

Sen çalışırken başka biri main branch’e yeni değişiklikler eklemiş olabilir. Bu yüzden kendi branch’ini güncel tutmak gerekir.

Önce GitHub’daki son durumu bilgisayarına çek:

bash git fetch origin 

Sonra main branch’teki güncel değişiklikleri kendi branch’ine birleştir:

bash git merge origin/main 

Buradaki mantık:

- git fetch origin: GitHub’daki son branch bilgilerini indirir ama çalışma dosyalarını değiştirmez.
- git merge origin/main: GitHub’daki güncel main branch’i senin aktif branch’inle birleştirir.

Bu adımın amacı, PR açmadan önce kendi branch’inin güncel main ile uyumlu olduğundan emin olmaktır.

Eğer conflict çıkarsa Git, hangi dosyalarda çakışma olduğunu söyler. O dosyaları düzenleyip conflict’i çözdükten sonra:

bash git add . git commit 

ile merge işlemini tamamlayabilirsin.

---

### 3. dbt proje klasörüne gir ve modelleri test et

Önce dbt projesinin olduğu klasöre gir:

bash cd superstore 

Bu projede klasör adı farklıysa, örneğin nova ise:

bash cd nova 

Sonra kendi modelini ve ona bağlı modelleri çalıştır:

bash uv run dbt build --select +my_mart 

Burada my_mart yerine kendi model adını yazmalısın.

Örnek:

bash uv run dbt build --select +mart_service_kpis 

Buradaki mantık:

- dbt build: Modeli çalıştırır, testleri çalıştırır, varsa snapshot/seed gibi ilgili adımları da yürütür.
- --select +my_mart: Seçtiğin modelle birlikte onun bağlı olduğu upstream modelleri de dahil eder.
- Baştaki +, “bu modelin ihtiyaç duyduğu önceki modelleri de çalıştır” anlamına gelir.

Yani sadece tek SQL dosyasını değil, o modelin bağlı olduğu zinciri de kontrol etmiş oluruz.

---

### 4. Her şey başarılıysa branch’i tekrar push et

Eğer dbt build başarılı olduysa ve son değişikliklerin commit’lendiyse branch’i GitHub’a gönder:

bash git push 

Eğer henüz commit atmadıysan önce:

bash git status 

ile değişikliklere bak.

Sonra:

bash git add . git commit -m "Add mart model" git push 

Commit mesajını yaptığın işe göre yazmalısın.

Örnek mesajlar:

bash git commit -m "Add service KPI mart" git commit -m "Add staging model for interactions" git commit -m "Fix source tests" 

---

### 5. GitHub’da Pull Request aç

GitHub’da repo’ya gir.

Sonra kendi branch’in için bir Pull Request aç:

text base: main compare: senin-branch-adin 

Örnek:

text base: main compare: drk-add-marts 

PR açıklamasında kısaca şunları yazmak iyi olur:

text Ne yaptım? - Yeni mart modeli ekledim. - İlgili schema testlerini ekledim. - dbt build ile kontrol ettim.  Nasıl test ettim? - uv run dbt build --select +mart_service_kpis 

PR, yaptığın işi main branch’e eklemeden önce kontrol etmek için kullanılır.

---

### 6. PR merge edildikten sonra local main branch’ini güncelle

PR merge edildikten sonra kendi bilgisayarındaki main branch hâlâ eski olabilir. Bu yüzden güncellemek gerekir.

Önce main branch’e geç:

bash git checkout main 

Sonra GitHub’daki güncel main branch’i çek:

bash git pull 

Bu adımdan sonra bilgisayarındaki main, GitHub’daki güncel main ile aynı hale gelir.

---

### 7. Yeni iş için yeni branch aç

Her yeni iş için main branch’ten yeni bir branch açmak gerekir.

Önce main branch’te olduğundan ve güncel olduğundan emin ol:

bash git checkout main git pull 

Sonra yeni branch aç:

bash git checkout -b new-feat 

Branch adını yaptığın işe göre açıklayıcı seçmek daha iyi olur.

Örnek branch adları:

bash git checkout -b add-stg-users git checkout -b add-service-kpi-mart git checkout -b fix-source-tests git checkout -b add-retention-models 

---

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

Sonra GitHub’da PR açılır.

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

### 1. Doğrudan main branch’te çalışmamaya çalış

main branch projenin temiz ve çalışan hali olmalı. Yeni işler için ayrı branch açmak daha güvenli.

Yanlışlıkla main branch’teysen:

```bash 
git branch 
```

ile kontrol edebilirsin. Aktif branch’in yanında * işareti olur.

---

### 2. PR açmadan önce dbt build çalıştır

PR açmadan önce en azından kendi modelini ve bağlı modelleri test et:

```bash 
uv run dbt build --select +my_model 
```

Bu, bozuk SQL, eksik kaynak, başarısız test gibi hataları önceden yakalamamızı sağlar.

---

### 3. Branch’i güncel tut

PR açmadan önce:

```bash 
git fetch origin 
git merge origin/main 
````

yapmak iyi bir alışkanlıktır.

Böylece senin branch’in güncel main ile uyumlu olur.

---

## 4. Commit mesajlarını açıklayıcı yaz

Çok genel mesajlardan kaçın:

```bash 
git commit -m "update" 
git commit -m "changes" 
git commit -m "fix" 
```

Bunun yerine daha açıklayıcı yaz:

```bash 
git commit -m "Add staging model for users"
git commit -m "Add tests for transaction source" 
git commit -m "Create service KPI mart"
``` 


### 5. Hata çıkarsa önce git status çalıştır

Bir şey karışırsa ilk bakılacak komut:

bash git status 

Bu komut sana hangi branch’te olduğunu, hangi dosyaların değiştiğini ve Git’in senden ne beklediğini gösterir.