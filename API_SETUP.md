# 🔗 PHP API Entegrasyonu Kurulum Rehberi

GitHub Actions'tan çekilen veriyi PHP backend'ine otomatik göndermek için kurulum.

## 📋 Gereksinimler

- ✅ GitHub Actions workflow'u çalışıyor olmalı
- ✅ PHP backend hazır (`cron_job-5.php`)
- ✅ API endpoint'i ve anahtarı mevcut

## 🚀 Adım Adım Kurulum

### 1️⃣ GitHub Secrets Tanımla

1. **GitHub.com** → Repository → **Settings**
2. Sol menüden **Secrets and variables** → **Actions**
3. **New repository secret** butonuna tıkla

**İlk Secret:**
- **Name:** `API_ENDPOINT`
- **Value:** `https://seninsitendomain.com/cron_job-5.php`
- **Add secret** tıkla

**İkinci Secret:**
- **Name:** `API_KEY`
- **Value:** `.yasa_env` dosyandaki `PUSH_KEY` değeri
- **Add secret** tıkla

### 2️⃣ PHP Dosyasını Uyarla

`cron_job-5.php` dosyasında şu değişiklikleri yap:

#### Değişiklik 1: Alan İsimlerini Uyarla (Satır 137-142)

**Eski:**
```php
$title       = $proposal['baslik'] ?? 'Başlık Yok';
$detailUrl   = $proposal['link'] ?? '';
$esasNo      = $proposal['esasNo'] ?? '';
$contentText = $proposal['metin'] ?? '';
$donem       = $proposal['donemYasamaYili'] ?? '';
```

**Yeni:**
```php
$title       = $proposal['baslik'] ?? 'Başlık Yok';
$detailUrl   = $proposal['link'] ?? '';
$esasNo      = $proposal['esas_no'] ?? $proposal['esasNo'] ?? ''; // Hem eski hem yeni format
$contentText = $proposal['metin'] ?? $proposal['durum'] ?? ''; // Metin yoksa durum kullan
$donem       = $proposal['donemYasamaYili'] ?? $proposal['sira'] ?? ''; // Dönem yoksa sıra
```

#### Değişiklik 2: İçerik Kontrolünü Gevşet (Satır 143-148)

**Eski:**
```php
// Link ve içerik mutlaka olmalı
if (empty($detailUrl) || empty($contentText)) {
    log_message("-- UYARI: Link veya içerik eksik, atlanıyor: " . ($title ?: 'İsimsiz'));
    $skippedCount++;
    continue;
}
```

**Yeni:**
```php
// Link mutlaka olmalı, içerik opsiyonel
if (empty($detailUrl)) {
    log_message("-- UYARI: Link eksik, atlanıyor: " . ($title ?: 'İsimsiz'));
    $skippedCount++;
    continue;
}

// İçerik yoksa placeholder kullan
if (empty($contentText)) {
    $contentText = "İçerik detayları: " . ($proposal['durum'] ?? 'Bilgi yok');
    log_message("-- UYARI: İçerik metni yok, placeholder kullanılıyor");
}
```

### 3️⃣ Test Et (Local)

Terminal'den test:

```bash
cd /Users/sungu/tbmm-scraper

# JSON'u PHP'ye gönder
curl -X POST https://seninsitendomain.com/cron_job-5.php \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: SENIN_API_KEYIN" \
  -d @scraper/data/kanun_teklifleri_sorgu.json
```

### 4️⃣ Workflow'u Çalıştır

1. **GitHub** → **Actions** → **TBMM Kanun Teklifleri Scraper**
2. **Run workflow** → **Run workflow**
3. Logları izle, "PHP API'ye veri gönder" adımını kontrol et

## 📊 Veri Formatı Karşılaştırması

### Mevcut JSON (Scraper Çıktısı)
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

### PHP Beklentisi (Güncelleme Sonrası)
```php
[
  'baslik'           => string,  // ✅ Mevcut
  'link'             => string,  // ✅ Mevcut
  'esas_no/esasNo'   => string,  // ✅ İkisi de desteklenir
  'metin'            => string,  // ⚠️ Yoksa durum kullanılır
  'donemYasamaYili'  => string,  // ⚠️ Yoksa sira kullanılır
]
```

## 🔧 İleri Seviye: Metin Çekme

Eğer her teklifin tam içeriğini çekmek istersen:

### Seçenek A: PDF İçeriğini Çek

Scraper'a PDF parse özelliği ekle (PyPDF2 ile):

```python
# kanun_teklifleri_scraper.py'a ekle
import PyPDF2
import requests
from io import BytesIO

def extract_pdf_text(pdf_url):
    try:
        response = requests.get(pdf_url)
        pdf_file = BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"PDF parse hatası: {e}")
        return ""
```

### Seçenek B: HTML Detay Sayfası Çek

Eğer PDF değil de HTML detay sayfası varsa:

```python
def scrape_detail_page(detail_url):
    html = fetch_page(detail_url)
    soup = BeautifulSoup(html, 'lxml')
    content = soup.select_one('.kanun-metni, .teklif-metni')
    return content.get_text() if content else ""
```

## 🐛 Sorun Giderme

### API Çağrısı Başarısız

**Hata:** `curl: (6) Could not resolve host`

**Çözüm:**
- API_ENDPOINT doğru mu kontrol et
- HTTPS mi HTTP mi kontrol et

### 403 Forbidden

**Hata:** `Forbidden. Invalid or missing API key`

**Çözüm:**
- API_KEY GitHub Secrets'ta doğru tanımlı mı?
- `.yasa_env` dosyasındaki PUSH_KEY ile aynı mı?

### 400 Bad Request

**Hata:** `Bad Request. Invalid JSON format`

**Çözüm:**
- JSON dosyası bozuk olabilir
- `cat scraper/data/kanun_teklifleri_sorgu.json | jq` ile validate et

### 500 Internal Server Error

**Hata:** Sunucu hatası

**Çözüm:**
- PHP loglarını kontrol et (`receiver.log`)
- Veritabanı bağlantısını test et

## 📈 Başarı Metrikleri

Başarılı kurulum sonrası:

- ✅ GitHub Actions her çalışmada PHP'ye veri gönderir
- ✅ PHP'de `new`, `updated`, `skipped` sayıları loglanır
- ✅ Veritabanında teklifler otomatik güncellenir
- ✅ AI özetleri otomatik oluşturulur (Gemini API varsa)

## 📊 Monitoring

### GitHub Actions Logları

```
🌐 PHP API'ye veri gönderiliyor...
📍 Endpoint: https://example.com/cron_job-5.php
📊 HTTP Status: 200
📄 Response: {"status":"success","message":"İşlem tamamlandı...","new":5,"updated":3,"skipped":2}
✅ Veri başarıyla PHP API'ye gönderildi!
```

### PHP Logları (receiver.log)

```
[2025-11-07 12:00:15] Gelen veri doğrulandı. 10 adet kanun teklifi işlenecek.
[2025-11-07 12:00:16] İşleniyor: (2/1234) Eğitim Kanunu Değişikliği
[2025-11-07 12:00:16] -- AI özeti üretildi.
[2025-11-07 12:00:17] -- Veritabanına YENİ KAYIT EKLENDİ.
...
[2025-11-07 12:00:25] İşlem tamamlandı. Yeni: 5, Güncellenen: 3, Atlanan: 2
```

## 🎯 Sonraki Adımlar

1. ✅ GitHub Secrets tanımla
2. ✅ PHP dosyasını güncelle
3. ✅ Local test yap
4. ✅ GitHub Actions'tan test et
5. ⭐ İsteğe bağlı: PDF metin çekme ekle

---

**Tebrikler!** Artık tam otomatik bir veri pipeline'ınız var! 🎉

