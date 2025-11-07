# ✅ GitHub Actions Kurulum Kontrol Listesi

Bu dosya, TBMM Kanun Teklifleri Scraper'ı GitHub Actions ile otomatik çalıştırmak için yapmanız gerekenleri adım adım açıklar.

## 🎯 Hedef

Her gün otomatik olarak TBMM Kanun Teklifleri sayfasından veri çeken, sonuçları JSON formatında kaydeden ve GitHub repository'sine commit eden bir sistem.

## 📋 Yapılacaklar Listesi

### 1. ✅ Dosyalar Hazır

Aşağıdaki dosyalar projenize eklendi:

- [x] `.github/workflows/scrape-kanun-teklifleri.yml` - GitHub Actions workflow
- [x] `scraper/kanun_teklifleri_scraper.py` - Ana scraper kodu
- [x] `scraper/requirements.txt` - Python bağımlılıkları
- [x] `GITHUB_ACTIONS_SETUP.md` - Detaylı kurulum rehberi
- [x] `scraper/README_KANUN_TEKLIFLERI.md` - Scraper dokümantasyonu
- [x] `.gitignore` - Güncellenmiş (Chrome profilleri vs.)
- [x] `README.md` - Ana README güncellendi

### 2. 🔄 GitHub'a Push

```bash
# Tüm değişiklikleri commit edin
git add .
git commit -m "🤖 GitHub Actions ile otomatik TBMM scraper eklendi"
git push origin master
```

### 3. ⚙️ GitHub Repository Ayarları

GitHub repository'nizde **Settings** > **Actions** > **General** sayfasına gidin:

#### Workflow İzinleri

1. **Workflow permissions** bölümünde:
   - ✅ `Read and write permissions` seçin
   - ✅ `Allow GitHub Actions to create and approve pull requests` işaretleyin
2. **Save** butonuna tıklayın

**Ekran görüntüsü referansı:**
```
[•] Read and write permissions
    Workflows have read and write permissions in the repository.

[✓] Allow GitHub Actions to create and approve pull requests
```

### 4. 🚀 İlk Test Çalıştırması

#### Manuel Başlatma (Önerilen)

1. GitHub repository'nize gidin
2. **Actions** sekmesine tıklayın
3. Sol menüden **"TBMM Kanun Teklifleri Scraper"** workflow'unu seçin
4. Sağ üstte **"Run workflow"** dropdown'una tıklayın
5. **"Run workflow"** yeşil butonuna tıklayın
6. Workflow başlayacak, işlem yaklaşık 1-2 dakika sürer

#### Sonuçları Kontrol Etme

1. Workflow çalışmasına tıklayın
2. **scrape** job'una tıklayın
3. Her adımı genişleterek logları inceleyin
4. Özellikle şu adımlara dikkat edin:
   - ✅ Chrome kurulumu
   - ✅ Scraper çalıştırma
   - ✅ Veri istatistikleri
   - ✅ Commit işlemi

### 5. 📊 Veriyi Kontrol Etme

Workflow başarılı olduysa:

1. Repository ana sayfasına dönün
2. `scraper/data/kanun_teklifleri_sorgu.json` dosyasını görmelisiniz
3. Dosyayı açın, JSON verisini kontrol edin
4. Son commit mesajında "🤖 Otomatik veri güncelleme" yazmalı

**Örnek JSON yapısı:**
```json
[
  {
    "sira": "28/4",
    "baslik": "...",
    "esas_no": "...",
    "link": "https://cdn.tbmm.gov.tr/...",
    "durum": "...",
    "cekme_tarihi": "2025-11-07T..."
  }
]
```

### 6. ⏰ Otomatik Zamanlama

Workflow artık her gün **saat 12:00 (Türkiye saati)** otomatik çalışacak.

**Zamanlamayı değiştirmek için:**

`.github/workflows/scrape-kanun-teklifleri.yml` dosyasında:

```yaml
schedule:
  - cron: '0 9 * * *'  # 09:00 UTC = 12:00 TR
```

**Örnekler:**
- Her 6 saatte: `'0 */6 * * *'`
- Her gece yarısı: `'0 21 * * *'` (00:00 TR = 21:00 UTC)
- Haftada bir Pazartesi: `'0 9 * * 1'`

[Cron ifadesi oluşturucu](https://crontab.guru/)

## 🎉 Başarı Kriterleri

Kurulum başarılı sayılır eğer:

- ✅ Workflow hatasız çalışıyor
- ✅ `scraper/data/kanun_teklifleri_sorgu.json` oluşturuldu
- ✅ Dosya en az 1 teklif içeriyor (array length > 0)
- ✅ Veriler otomatik commit edildi
- ✅ Actions sekmesinde yeşil ✅ işareti görünüyor

## 🐛 Sorun Giderme

### Workflow Görünmüyor

**Sorun:** Actions sekmesinde workflow yok

**Çözüm:**
1. `.github/workflows/scrape-kanun-teklifleri.yml` dosyasının doğru yerde olduğunu kontrol edin
2. YAML syntax hatası olup olmadığını kontrol edin ([YAML Validator](https://www.yamllint.com/))
3. Repository'yi yenileyin (F5)

### Workflow Devre Dışı

**Sorun:** "Workflows are disabled" mesajı

**Çözüm:**
- Repository fork edilmişse, Actions sekmesinde "Enable workflows" butonuna tıklayın

### Commit İzni Hatası

**Sorun:** `refusing to allow a GitHub App to create or update workflow` veya `permission denied`

**Çözüm:**
1. Settings > Actions > General
2. **Workflow permissions** kısmından "Read and write permissions" seçin
3. Save edin ve workflow'u yeniden çalıştırın

### Scraper Hataları

**Sorun:** Scraper çalışıyor ama veri çekemiyor

**Çözüm:**
1. Local'de test edin:
   ```bash
   cd scraper
   python kanun_teklifleri_scraper.py
   ```
2. Hata mesajlarını inceleyin
3. Bot koruması aktif olabilir - `REQUEST_DELAY` değerini artırın

### Chrome Hatası

**Sorun:** ChromeDriver veya Chrome bulunamıyor

**Çözüm:**
- Workflow'daki Chrome kurulum adımını kontrol edin
- Chrome versiyonunu güncelleyin

## 📚 İleri Adımlar

### 1. Farklı Sorgular Ekleyin

`scraper/kanun_teklifleri_scraper.py` içinde `fill_search_form()` parametrelerini değiştirin:

```python
# Sadece kanunlaşmış teklifler
fill_search_form(
    arama_kelime="",
    donem="Son Dönem",
    durum="KANUNLAŞTI"
)
```

### 2. Veri Analizi Ekleyin

Workflow'a analiz adımı ekleyin (isteğe bağlı)

### 3. Notification Ekleyin

Slack/Discord/Email bildirimleri ekleyin

### 4. GitHub Pages API

GitHub Pages aktif ederek veriye API gibi erişin:

```
https://KULLANICI_ADI.github.io/tbmm-scraper/scraper/data/kanun_teklifleri_sorgu.json
```

## 🔗 Faydalı Linkler

- [GitHub Actions Dokümantasyonu](https://docs.github.com/en/actions)
- [Detaylı Kurulum Rehberi](GITHUB_ACTIONS_SETUP.md)
- [Scraper Kullanım Kılavuzu](scraper/README_KANUN_TEKLIFLERI.md)
- [Cron Expression Generator](https://crontab.guru/)

## ✉️ Destek

Sorun yaşıyorsanız:
1. [GitHub Issues](../../issues) açın
2. Hata mesajlarını paylaşın
3. Workflow loglarını ekleyin

---

**Tebrikler!** 🎉 Artık otomatik çalışan bir TBMM veri toplama sisteminiz var!

