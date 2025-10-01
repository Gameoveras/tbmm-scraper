# GitHub Secrets Yapılandırması

Bu proje GitHub Actions kullanarak TBMM'den veri çeker ve sunucunuza gönderir. Bunun için aşağıdaki GitHub Secrets'ı yapılandırmanız gerekiyor.

## Gerekli Secrets

### 1. `PUSH_API_KEY`
- **Açıklama**: Sunucunuza veri göndermek için kullanılan güvenlik anahtarı
- **Değer**: `.yasa_env` dosyanızdaki `PUSH_KEY` değeri
- **Örnek**: `f9G7v2XkL8pZqT1sY4rH6mN0bC5jD3wQ`

### 2. `RECEIVER_URL`
- **Açıklama**: Verilerin gönderileceği sunucu endpoint adresi
- **Değer**: `cron_job.php` dosyanızın tam URL'si
- **Örnek**: `https://example.com/cron_job.php`

## Nasıl Eklenir?

1. GitHub repository'nize gidin
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** butonuna tıklayın
4. Her bir secret için:
   - **Name**: Yukarıdaki secret adını girin (örn: `PUSH_API_KEY`)
   - **Value**: İlgili değeri girin
   - **Add secret** butonuna tıklayın

## Workflow'u Test Etme

Secrets'ları ekledikten sonra:

1. **Actions** sekmesine gidin
2. **TBMM Scrape & Push** workflow'unu seçin
3. **Run workflow** butonuna tıklayın
4. İsteğe bağlı olarak dönem numarasını değiştirin
5. **Run workflow** ile başlatın

## Otomatik Çalışma

Workflow varsayılan olarak **her 6 saatte bir** otomatik çalışır. Bunu değiştirmek için:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Her 6 saatte bir
```

### Cron Zamanlaması Örnekleri:
- `0 */3 * * *` - Her 3 saatte bir
- `0 9,21 * * *` - Günde 2 kez (09:00 ve 21:00)
- `0 0 * * *` - Günde 1 kez (gece yarısı)

## Sorun Giderme

### "Forbidden. Invalid or missing API key" hatası
- `PUSH_API_KEY` secret'ının doğru girildiğinden emin olun
- `.yasa_env` dosyasındaki `PUSH_KEY` ile aynı olmalı

### "Connection refused" veya timeout hataları
- `RECEIVER_URL` adresinin doğru ve erişilebilir olduğundan emin olun
- Sunucunuzun HTTP POST isteklerini kabul ettiğinden emin olun

### Scraper hiç veri bulamıyor
- TBMM sitesinin yapısı değişmiş olabilir
- `scraper/tbmm_scraper.py` dosyasındaki CSS selector'ları güncellemeniz gerekebilir

