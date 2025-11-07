# TBMM Kanun Teklifleri Scraper

Bu scraper, TBMM web sitesindeki [Kanun Teklifleri Sorgu](https://www.tbmm.gov.tr/yasama/kanun-teklifleri) sayfasından veri çeker.

## Özellikler

- ✅ Selenium ile dinamik sayfa yükleme
- ✅ Sorgu formu otomatik doldurma
- ✅ Arama filtrelerini destekler (kelime, dönem, durum)
- ✅ Sayfalama (pagination) desteği
- ✅ JSON formatında veri kaydetme
- ✅ Bot korumasını aşma teknikleri
- ✅ Hata yönetimi ve logging

## Kurulum

### 1. Python Bağımlılıklarını Yükle

```bash
cd scraper
pip install -r requirements.txt
```

### 2. Chrome Driver Kurulumu

Selenium Chrome WebDriver kullanır. İki seçeneğiniz var:

#### Otomatik (Önerilen):
Selenium 4.x otomatik olarak ChromeDriver'ı indirir, herhangi bir işlem yapmanıza gerek yok.

#### Manuel:
```bash
# macOS (Homebrew ile)
brew install chromedriver

# Linux (apt ile)
sudo apt-get install chromium-chromedriver

# Manuel indirme
# https://chromedriver.chromium.org/downloads adresinden indirip PATH'e ekle
```

## Kullanım

### Temel Kullanım

Tüm sonuçları çekmek için:

```bash
python kanun_teklifleri_scraper.py
```

### Parametreleri Özelleştirme

Script içindeki `main()` fonksiyonunda `fill_search_form()` parametrelerini değiştirebilirsiniz:

```python
# Örnek 1: Belirli bir kelime ara
fill_search_form(
    arama_kelime="eğitim",
    donem="Son Dönem",
    durum=""
)

# Örnek 2: Sadece kanunlaşmış teklifler
fill_search_form(
    arama_kelime="",
    donem="Son Dönem",
    durum="KANUNLAŞTI"
)

# Örnek 3: Belirli dönem
fill_search_form(
    arama_kelime="",
    donem="28.DÖNEM 3.Yasama Yılı",
    durum=""
)
```

### Headless Mode'u Kapatma (Tarayıcıyı Görmek İçin)

Script varsayılan olarak headless mode'da çalışır (tarayıcı görünmez). Tarayıcıyı görmek isterseniz:

`kanun_teklifleri_scraper.py` dosyasında 52. satırı yorum satırı yapın:

```python
# chrome_options.add_argument('--headless=new')  # Bu satırı yorum yap
```

## Çıktı

Script çalıştığında:

1. `data/` klasörünü oluşturur
2. TBMM sitesine bağlanır
3. Sorgu formunu doldurur
4. Tüm sayfalardaki sonuçları toplar
5. `data/kanun_teklifleri_sorgu.json` dosyasına kaydeder

### JSON Çıktı Formatı

```json
[
  {
    "sira": "1",
    "baslik": "Kanun Teklifi Başlığı",
    "link": "https://www.tbmm.gov.tr/...",
    "esas_no": "2/1234",
    "donem": "28. Dönem",
    "durum": "KANUNLAŞTI",
    "cekme_tarihi": "2025-11-07T10:30:00"
  },
  ...
]
```

## Örnek Çıktı

```bash
[2025-11-07 10:30:00] INFO: 🚀 TBMM Kanun Teklifleri Sorgu Scraper başlatıldı
[2025-11-07 10:30:00] INFO: ✅ Veri dizini hazır: data
[2025-11-07 10:30:00] INFO: 🚀 Selenium WebDriver başlatılıyor...
[2025-11-07 10:30:02] INFO: ✅ WebDriver başarıyla başlatıldı
[2025-11-07 10:30:02] INFO: 🌐 Sorgu sayfası açılıyor: https://www.tbmm.gov.tr/yasama/kanun-teklifleri
[2025-11-07 10:30:08] INFO: 📝 Form dolduruluyor: kelime='', dönem='Son Dönem', durum=''
[2025-11-07 10:30:08] INFO:   ✓ Dönem seçildi: Son Dönem
[2025-11-07 10:30:09] INFO: 🔍 Sorgu gönderiliyor...
[2025-11-07 10:30:12] INFO: ✅ Sorgu gönderildi
[2025-11-07 10:30:12] INFO: 📄 Sayfa 1 işleniyor...
[2025-11-07 10:30:13] INFO: 📊 Sonuçlar parse ediliyor...
[2025-11-07 10:30:13] INFO:   ✓ Tablo bulundu: table.table (52 satır)
[2025-11-07 10:30:13] INFO: ✅ 50 sonuç parse edildi
[2025-11-07 10:30:14] INFO:   ➡️  Sonraki sayfaya geçiliyor...
[2025-11-07 10:30:17] INFO: 📄 Sayfa 2 işleniyor...
...
[2025-11-07 10:35:00] INFO: ✅ Tüm sayfalar tarandı (Toplam 10 sayfa)
[2025-11-07 10:35:00] INFO: 💾 Veriler kaydedildi: data/kanun_teklifleri_sorgu.json (485 kayıt)
[2025-11-07 10:35:00] INFO: ✅ Scraping tamamlandı! Toplam: 485 kayıt

[2025-11-07 10:35:00] INFO: 📊 İstatistikler:
[2025-11-07 10:35:00] INFO:   • Toplam kayıt: 485
[2025-11-07 10:35:00] INFO:   • Durum dağılımı:
[2025-11-07 10:35:00] INFO:     - İŞLEMDE: 234
[2025-11-07 10:35:00] INFO:     - KANUNLAŞTI: 156
[2025-11-07 10:35:00] INFO:     - KOMİSYONDA: 95
```

## Sorun Giderme

### ChromeDriver Hatası
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**Çözüm:** Chrome ve ChromeDriver'ın yüklü olduğundan emin olun.

### Bot Koruması
Site bazen bot koruması devreye alabilir. Bu durumda:

1. `time.sleep()` sürelerini artırın
2. Headless mode'u kapatın
3. `REQUEST_DELAY` değerini artırın (örn: 5 saniye)

### Tablo Bulunamadı
Eğer "Sonuç tablosu bulunamadı" hatası alırsanız:

1. `debug_page.html` dosyası oluşturulur
2. Bu dosyayı tarayıcıda açıp sayfa yapısını inceleyin
3. Gerekirse `parse_results_table()` fonksiyonundaki selector'ları güncelleyin

## İleri Seviye Kullanım

### Çoklu Sorgu Çalıştırma

Farklı parametrelerle birden fazla sorgu çalıştırmak için:

```python
# kanun_teklifleri_batch.py
from kanun_teklifleri_scraper import *

queries = [
    {"arama_kelime": "eğitim", "donem": "Son Dönem", "durum": ""},
    {"arama_kelime": "sağlık", "donem": "Son Dönem", "durum": ""},
    {"arama_kelime": "", "donem": "Son Dönem", "durum": "KANUNLAŞTI"},
]

for i, query in enumerate(queries):
    logger.info(f"\n{'='*50}")
    logger.info(f"Sorgu {i+1}/{len(queries)}: {query}")
    logger.info(f"{'='*50}\n")
    
    # Her sorgu için ayrı dosya
    OUTPUT_FILE = f"data/sorgu_{i+1}.json"
    
    # ... main() içeriğini buraya kopyalayın ...
```

## Lisans

MIT License - Detaylar için üst dizindeki LICENSE dosyasına bakın.

## İletişim

Sorularınız için issue açabilirsiniz.

