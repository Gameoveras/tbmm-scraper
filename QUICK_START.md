# 🚀 Hızlı Başlangıç - TBMM Otomatik Scraper

## 📌 Özet

TBMM Kanun Teklifleri sayfasından otomatik veri toplayan, GitHub Actions ile her gün çalışan bir sistem kuruldu.

## ⚡ 5 Dakikada Başla

### 1️⃣ GitHub'a Yükle

```bash
cd /Users/sungu/tbmm-scraper

# Dosyaları ekle
git add .

# Commit yap
git commit -m "🤖 GitHub Actions ile otomatik TBMM scraper eklendi

- Selenium tabanlı Python scraper
- Her gün saat 12:00'de otomatik çalışma
- JSON formatında veri kaydetme
- Bot koruması bypass
"

# Push et
git push origin master
```

### 2️⃣ GitHub Ayarları

1. GitHub repository'nize gidin
2. **Settings** > **Actions** > **General**
3. **Workflow permissions** bölümünde:
   - ✅ `Read and write permissions` seçin
   - ✅ `Allow GitHub Actions to create and approve pull requests` işaretleyin
4. **Save**

### 3️⃣ İlk Test

1. **Actions** sekmesine git
2. **TBMM Kanun Teklifleri Scraper** seç
3. **Run workflow** > **Run workflow**
4. 1-2 dakika bekle
5. ✅ Yeşil işaret görmelisin

### 4️⃣ Veriyi Kontrol Et

Repository'de `scraper/data/kanun_teklifleri_sorgu.json` dosyası oluşmuş olmalı.

```bash
# Local'de kontrol
cat scraper/data/kanun_teklifleri_sorgu.json | python3 -m json.tool | head -50
```

## ✅ Başarı!

Artık her gün saat 12:00'de otomatik veri çekiliyor! 🎉

---

## 📖 Detaylı Dokümantasyon

- [Kurulum Kontrol Listesi](SETUP_CHECKLIST.md) - Adım adım kurulum
- [GitHub Actions Rehberi](GITHUB_ACTIONS_SETUP.md) - Detaylı yapılandırma
- [Scraper Kullanımı](scraper/README_KANUN_TEKLIFLERI.md) - Python scraper detayları

## 🔧 Özelleştirme

### Zamanlamayı Değiştir

`.github/workflows/scrape-kanun-teklifleri.yml`:
```yaml
schedule:
  - cron: '0 9 * * *'  # Her gün 12:00 TR
```

### Sorgu Parametrelerini Değiştir

`scraper/kanun_teklifleri_scraper.py`:
```python
fill_search_form(
    arama_kelime="",         # Aranacak kelime
    donem="Son Dönem",       # Dönem
    durum=""                 # KANUNLAŞTI, İŞLEMDE, vb.
)
```

## 🎯 Oluşturulan Dosyalar

```
tbmm-scraper/
├── .github/workflows/
│   └── scrape-kanun-teklifleri.yml     ← GitHub Actions workflow
├── scraper/
│   ├── kanun_teklifleri_scraper.py     ← Ana scraper
│   ├── README_KANUN_TEKLIFLERI.md      ← Scraper dokümantasyonu
│   └── data/
│       └── kanun_teklifleri_sorgu.json ← Çekilen veriler
├── GITHUB_ACTIONS_SETUP.md             ← Detaylı kurulum
├── SETUP_CHECKLIST.md                  ← Kontrol listesi
├── QUICK_START.md                      ← Bu dosya
└── README.md                           ← Güncellendi
```

## 🆘 Yardım

### Local'de Test

```bash
cd scraper
pip install -r requirements.txt
python kanun_teklifleri_scraper.py
```

### Sorun mu Var?

1. [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) - Sorun giderme bölümü
2. GitHub Actions loglarını incele
3. Issue aç

## 📊 Veri Formatı

```json
[
  {
    "sira": "28/4",
    "baslik": "Kanun Teklifi Başlığı",
    "link": "https://cdn.tbmm.gov.tr/...",
    "esas_no": "05/11/2025",
    "durum": "KOMİSYONDA",
    "cekme_tarihi": "2025-11-07T19:21:34.788575"
  }
]
```

## 🎊 Özellikler

✅ **Otomatik**: Her gün saat 12:00 çalışır  
✅ **Güvenilir**: Hata durumunda yeniden dener  
✅ **Şeffaf**: Tüm loglar GitHub Actions'da  
✅ **Versiyon Kontrol**: Tüm değişiklikler git'te  
✅ **Kolay**: Hiçbir sunucu yönetimine gerek yok  

---

**Hazır!** Artık otomatik TBMM veri toplama sisteminiz çalışıyor! 🚀

