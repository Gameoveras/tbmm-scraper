# 🤖 GitHub Actions ile Otomatik Scraping Kurulumu

Bu dokümantasyon, TBMM Kanun Teklifleri Scraper'ın GitHub Actions ile otomatik olarak çalışmasını sağlayan kurulum rehberidir.

## 📋 Özellikler

✅ **Otomatik Zamanlama**: Her gün saat 12:00 (Türkiye saati) otomatik çalışır  
✅ **Manuel Tetikleme**: İstediğiniz zaman manuel başlatabilirsiniz  
✅ **Otomatik Commit**: Yeni veriler otomatik olarak repository'ye commit edilir  
✅ **Hata Yönetimi**: Hata durumunda bildirim ve log kayıtları  
✅ **Artifact Yedekleme**: Her çalışmanın sonucu 30 gün boyunca saklanır  
✅ **Headless Mode**: Sunucu ortamında görsel arayüz olmadan çalışır  

## 🚀 Kurulum Adımları

### 1. Repository İzinlerini Ayarla

GitHub repository'nizin Settings bölümünden:

1. **Settings** > **Actions** > **General**
2. **Workflow permissions** bölümünde:
   - ✅ `Read and write permissions` seçin
   - ✅ `Allow GitHub Actions to create and approve pull requests` işaretleyin
3. **Save** butonuna tıklayın

### 2. Workflow Dosyasını Kontrol Et

`.github/workflows/scrape-kanun-teklifleri.yml` dosyası zaten oluşturulmuş durumda. Bu dosya:

- Her gün saat 09:00 UTC'de çalışır (Türkiye saati 12:00)
- Manuel tetiklenebilir
- Kod değişikliklerinde test olarak çalışır

### 3. İlk Çalıştırma

#### Otomatik (Zamanlanmış)
Workflow ilk kez yarın saat 12:00'de otomatik çalışacak.

#### Manuel Başlatma
Hemen test etmek için:

1. GitHub repository'nize gidin
2. **Actions** sekmesine tıklayın
3. Sol menüden **TBMM Kanun Teklifleri Scraper** workflow'unu seçin
4. **Run workflow** > **Run workflow** butonuna tıklayın

## ⚙️ Yapılandırma

### Çalışma Zamanını Değiştirme

`.github/workflows/scrape-kanun-teklifleri.yml` dosyasında cron ifadesini düzenleyin:

```yaml
schedule:
  - cron: '0 9 * * *'  # Her gün 09:00 UTC (12:00 TR)
```

**Örnekler:**
```yaml
# Her 6 saatte bir
- cron: '0 */6 * * *'

# Her Pazartesi saat 10:00 UTC
- cron: '0 10 * * 1'

# Haftaiçi her gün saat 08:00 UTC
- cron: '0 8 * * 1-5'

# Her 12 saatte bir (sabah ve akşam)
- cron: '0 0,12 * * *'
```

Cron ifadelerini oluşturmak için: [crontab.guru](https://crontab.guru/)

### Sorgu Parametrelerini Değiştirme

`scraper/kanun_teklifleri_scraper.py` dosyasında `main()` fonksiyonundaki `fill_search_form()` parametrelerini düzenleyin:

```python
# Örnek: Sadece kanunlaşmış teklifler
fill_search_form(
    arama_kelime="",
    donem="Son Dönem",
    durum="KANUNLAŞTI"
)

# Örnek: Belirli bir kelime
fill_search_form(
    arama_kelime="eğitim",
    donem="Son Dönem",
    durum=""
)
```

## 📊 Çalışma Durumunu İzleme

### Actions Sekmesi

1. Repository'nize gidin
2. **Actions** sekmesine tıklayın
3. Son çalıştırmaları göreceksiniz:
   - ✅ Yeşil: Başarılı
   - ❌ Kırmızı: Başarısız
   - 🟡 Sarı: Çalışıyor

### Detaylı Log İnceleme

1. Bir workflow çalışmasına tıklayın
2. **scrape** job'una tıklayın
3. Her adımın detaylı loglarını görebilirsiniz

### Artifacts (Yedekler)

Her çalışmanın sonucu Artifacts olarak saklanır:

1. Workflow çalışmasına gidin
2. Sayfanın altında **Artifacts** bölümünü bulun
3. `kanun-teklifleri-data-XXX` dosyasını indirin

## 📈 Veri Erişimi

### JSON Dosyası

Çekilen veriler `scraper/data/kanun_teklifleri_sorgu.json` dosyasında tutulur ve her çalışmada güncellenir.

### Raw Data Erişimi

```bash
# GitHub üzerinden direkt erişim
https://raw.githubusercontent.com/KULLANICI_ADI/tbmm-scraper/master/scraper/data/kanun_teklifleri_sorgu.json
```

### API Benzeri Kullanım

GitHub Pages ile birlikte kullanarak basit bir API oluşturabilirsiniz:

1. Repository Settings > Pages > Source: `master branch`
2. Veriye erişim:
```
https://KULLANICI_ADI.github.io/tbmm-scraper/scraper/data/kanun_teklifleri_sorgu.json
```

## 🔔 Bildirimler

### E-posta Bildirimleri

GitHub otomatik olarak başarısız workflow'lar için e-posta gönderir.

### Slack/Discord Entegrasyonu

Workflow'a notification step'i ekleyebilirsiniz:

```yaml
- name: 📬 Slack bildirimi
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

## 🐛 Sorun Giderme

### Workflow Çalışmıyor

**Neden:** Repository fork edilmişse, workflow'lar varsayılan olarak devre dışıdır.

**Çözüm:**
1. Actions sekmesine gidin
2. "I understand my workflows, go ahead and enable them" butonuna tıklayın

### Commit İzni Hatası

**Hata:** `permission denied` veya `403 error`

**Çözüm:**
1. Settings > Actions > General
2. Workflow permissions kısmında "Read and write permissions" seçin

### ChromeDriver Hatası

**Hata:** `chromedriver not found` veya `session not created`

**Çözüm:** Workflow'daki Chrome kurulum step'i zaten bu sorunu çözüyor. Eğer hala sorun varsa, workflow dosyasında Chrome versiyonunu güncelleyin.

### Bot Koruması

**Hata:** Sayfa yüklenmiyor veya bot koruması devrede

**Çözüm:**
1. `REQUEST_DELAY` değerini artırın (örn: 5 saniye)
2. `time.sleep()` sürelerini uzatın
3. User-agent'i güncelleyin

### Veri Çekilemiyor

**Debug için:**

1. Workflow'a debug step ekleyin:

```yaml
- name: 🐛 Debug - Sayfa içeriğini kaydet
  if: failure()
  run: |
    if [ -f scraper/debug_page.html ]; then
      echo "Debug page oluşturuldu"
    fi
```

2. Local'de test edin:

```bash
cd scraper
python kanun_teklifleri_scraper.py
```

## 📝 İleri Seviye Kullanım

### Çoklu Sorgu

Farklı parametrelerle birden fazla scraping yapmak için:

1. Ayrı workflow dosyaları oluşturun veya
2. Script'i parametrize edin:

```python
import sys

if len(sys.argv) > 1:
    query_type = sys.argv[1]
    if query_type == "kanunlasmis":
        fill_search_form(durum="KANUNLAŞTI")
    elif query_type == "islemde":
        fill_search_form(durum="İŞLEMDE")
```

Workflow'da:
```yaml
- name: Sorgu 1
  run: python kanun_teklifleri_scraper.py kanunlasmis

- name: Sorgu 2
  run: python kanun_teklifleri_scraper.py islemde
```

### Veri Analizi

Workflow'a analiz adımı ekleyin:

```yaml
- name: 📊 Veri analizi
  run: |
    python -c "
    import json
    with open('scraper/data/kanun_teklifleri_sorgu.json', 'r') as f:
        data = json.load(f)
    print(f'Toplam: {len(data)} teklif')
    # Daha fazla analiz...
    "
```

### CSV Export

JSON'u CSV'ye çevirmek için:

```yaml
- name: 📄 CSV'ye çevir
  run: |
    python -c "
    import json, csv
    with open('scraper/data/kanun_teklifleri_sorgu.json', 'r') as f:
        data = json.load(f)
    with open('scraper/data/kanun_teklifleri.csv', 'w', encoding='utf-8') as f:
        if data:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    "
```

## 🔒 Güvenlik

- ❌ Workflow dosyasına API key veya şifre yazmayın
- ✅ Hassas bilgiler için GitHub Secrets kullanın
- ✅ Repository private ise, veriler de private kalır
- ✅ Public repository için veri gizliliğine dikkat edin

## 📚 Kaynaklar

- [GitHub Actions Dokümantasyonu](https://docs.github.com/en/actions)
- [Selenium Dokümantasyonu](https://www.selenium.dev/documentation/)
- [Cron Expression Generator](https://crontab.guru/)
- [TBMM Web Sitesi](https://www.tbmm.gov.tr)

## 🤝 Katkıda Bulunma

Sorun veya öneri için:
1. Issue açın
2. Pull request gönderin
3. Dokümantasyonu geliştirin

## 📞 Destek

Sorunlarınız için:
- GitHub Issues
- [TBMM API Dokümantasyonu](https://www.tbmm.gov.tr)

---

**Not:** Bu sistem eğitim ve araştırma amaçlıdır. TBMM web sitesinin kullanım şartlarına uygun kullanın ve sunucuya gereksiz yük bindirmekten kaçının.

