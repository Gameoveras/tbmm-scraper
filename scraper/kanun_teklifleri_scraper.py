#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TBMM Kanun Teklifleri Sorgu Scraper
Bu script TBMM web sitesindeki kanun teklifleri sorgu formunu kullanarak
sonuçları çeker ve JSON formatında kaydeder.
"""

import os
import json
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Sabitler
BASE_URL = "https://www.tbmm.gov.tr"
SORGU_URL = f"{BASE_URL}/yasama/kanun-teklifleri"
DATA_DIR = "data"
OUTPUT_FILE = f"{DATA_DIR}/kanun_teklifleri_sorgu.json"
REQUEST_DELAY = 2  # Saniye cinsinden bekleme süresi
TIMEOUT = 30

# Global WebDriver instance
driver = None


def create_data_directory():
    """Veri dizinini oluşturur"""
    os.makedirs(DATA_DIR, exist_ok=True)
    logger.info(f"✅ Veri dizini hazır: {DATA_DIR}")


def init_driver():
    """Selenium WebDriver'ı başlatır"""
    global driver
    
    if driver is not None:
        return driver
    
    logger.info("🚀 Selenium WebDriver başlatılıyor...")
    
    chrome_options = Options()
    
    # Headless mode - CI/CD ortamları için otomatik tespit
    # Local'de görmek istersen aşağıdaki satırı yorum yap
    is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'
    if is_ci:
        chrome_options.add_argument('--headless=new')
        logger.info("🤖 CI/CD ortamı tespit edildi, headless mode aktif")
    else:
        logger.info("💻 Local ortam, tarayıcı görünür olacak")
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # Unique user data directory to avoid conflicts
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix='chrome_profile_')
    chrome_options.add_argument(f'--user-data-dir={temp_dir}')
    
    # Bot tespitini zorlaştır
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Gerçek tarayıcı gibi davran
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # WebDriver özelliğini gizle
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("✅ WebDriver başarıyla başlatıldı")
        return driver
    except Exception as e:
        logger.error(f"❌ WebDriver başlatılamadı: {e}")
        raise


def close_driver():
    """Selenium WebDriver'ı kapatır"""
    global driver
    if driver is not None:
        try:
            driver.quit()
            driver = None
            logger.info("✅ WebDriver kapatıldı")
        except:
            pass


def wait_for_page_load(timeout=TIMEOUT):
    """Sayfanın tamamen yüklenmesini bekler"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(1)  # Ekstra güvenlik için
        return True
    except TimeoutException:
        logger.warning("⚠️ Sayfa yüklenme zaman aşımı")
        return False


def fill_search_form(arama_kelime="", donem="Son Dönem", durum=""):
    """
    Arama formunu doldurur ve sorguyu gönderir
    
    Args:
        arama_kelime: Aranacak kelime
        donem: Dönem seçimi (örn: "Son Dönem", "28.DÖNEM 3.Yasama Yılı")
        durum: Kanun durumu (örn: "", "KANUNLAŞTI", "İŞLEMDE", "KOMİSYONDA")
    """
    try:
        logger.info(f"📝 Form dolduruluyor: kelime='{arama_kelime}', dönem='{donem}', durum='{durum}'")
        
        # Arama kelimesi input'u
        if arama_kelime:
            try:
                # Muhtemel input field isimleri
                kelime_input = None
                possible_ids = ['txtArama', 'txtKelime', 'txtSearch', 'searchWord']
                
                for field_id in possible_ids:
                    try:
                        kelime_input = driver.find_element(By.ID, field_id)
                        break
                    except NoSuchElementException:
                        continue
                
                # ID ile bulamazsak name ile dene
                if not kelime_input:
                    possible_names = ['arama', 'kelime', 'search', 'q']
                    for field_name in possible_names:
                        try:
                            kelime_input = driver.find_element(By.NAME, field_name)
                            break
                        except NoSuchElementException:
                            continue
                
                if kelime_input:
                    kelime_input.clear()
                    kelime_input.send_keys(arama_kelime)
                    logger.info(f"  ✓ Arama kelimesi girildi: {arama_kelime}")
                else:
                    logger.warning("  ⚠️ Arama kelimesi input'u bulunamadı")
            except Exception as e:
                logger.warning(f"  ⚠️ Arama kelimesi hatası: {e}")
        
        # Dönem dropdown
        if donem:
            try:
                donem_select = None
                possible_ids = ['ddlDonem', 'ddlYasama', 'donem']
                
                for field_id in possible_ids:
                    try:
                        donem_select = Select(driver.find_element(By.ID, field_id))
                        break
                    except NoSuchElementException:
                        continue
                
                if donem_select:
                    # Önce visible text ile dene
                    try:
                        donem_select.select_by_visible_text(donem)
                        logger.info(f"  ✓ Dönem seçildi: {donem}")
                    except:
                        # Partial match dene
                        for option in donem_select.options:
                            if donem.lower() in option.text.lower():
                                donem_select.select_by_visible_text(option.text)
                                logger.info(f"  ✓ Dönem seçildi: {option.text}")
                                break
                else:
                    logger.warning("  ⚠️ Dönem dropdown'u bulunamadı")
            except Exception as e:
                logger.warning(f"  ⚠️ Dönem seçimi hatası: {e}")
        
        # Durum dropdown
        if durum:
            try:
                durum_select = None
                possible_ids = ['ddlDurum', 'ddlSonDurum', 'durum']
                
                for field_id in possible_ids:
                    try:
                        durum_select = Select(driver.find_element(By.ID, field_id))
                        break
                    except NoSuchElementException:
                        continue
                
                if durum_select:
                    try:
                        durum_select.select_by_visible_text(durum)
                        logger.info(f"  ✓ Durum seçildi: {durum}")
                    except:
                        # Partial match dene
                        for option in durum_select.options:
                            if durum.lower() in option.text.lower():
                                durum_select.select_by_visible_text(option.text)
                                logger.info(f"  ✓ Durum seçildi: {option.text}")
                                break
                else:
                    logger.warning("  ⚠️ Durum dropdown'u bulunamadı")
            except Exception as e:
                logger.warning(f"  ⚠️ Durum seçimi hatası: {e}")
        
        # Sorgula butonunu bul ve tıkla
        time.sleep(1)  # Form elemanlarının hazır olması için
        
        submit_button = None
        possible_button_ids = ['btnSorgula', 'btnAra', 'btnSearch', 'btnSubmit']
        possible_button_texts = ['SORGULA', 'ARA', 'Search', 'Submit']
        
        # ID ile dene
        for btn_id in possible_button_ids:
            try:
                submit_button = driver.find_element(By.ID, btn_id)
                break
            except NoSuchElementException:
                continue
        
        # Button text ile dene
        if not submit_button:
            for btn_text in possible_button_texts:
                try:
                    submit_button = driver.find_element(By.XPATH, f"//button[contains(text(), '{btn_text}')]")
                    break
                except NoSuchElementException:
                    try:
                        submit_button = driver.find_element(By.XPATH, f"//input[@type='submit' and contains(@value, '{btn_text}')]")
                        break
                    except NoSuchElementException:
                        continue
        
        # Type submit input dene
        if not submit_button:
            try:
                submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
            except NoSuchElementException:
                pass
        
        if submit_button:
            logger.info("🔍 Sorgu gönderiliyor...")
            submit_button.click()
            time.sleep(3)  # Sonuçların yüklenmesi için bekle
            wait_for_page_load()
            logger.info("✅ Sorgu gönderildi")
            return True
        else:
            logger.error("❌ Sorgula butonu bulunamadı!")
            # Debug için tüm butonları logla
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            all_inputs = driver.find_elements(By.XPATH, "//input[@type='submit' or @type='button']")
            logger.debug(f"Bulunan butonlar: {[btn.text for btn in all_buttons]}")
            logger.debug(f"Bulunan input'lar: {[inp.get_attribute('value') for inp in all_inputs]}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Form doldurma hatası: {e}")
        return False


def parse_results_table() -> List[Dict[str, str]]:
    """Sonuç tablosunu parse eder"""
    try:
        logger.info("📊 Sonuçlar parse ediliyor...")
        
        # Sayfanın HTML'ini al
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        results = []
        
        # Tabloyu bul - farklı selector'ları dene
        table = None
        table_selectors = [
            'table.sonucTablo',
            'table.listeTablo',
            'table.table',
            '#sonuclar table',
            '.sonuclar table',
            'table.gridview',
            'table[id*="Grid"]',
            'table'  # Son çare
        ]
        
        for selector in table_selectors:
            tables = soup.select(selector)
            if tables:
                # En büyük tabloyu al (muhtemelen sonuç tablosu)
                table = max(tables, key=lambda t: len(t.find_all('tr')))
                logger.info(f"  ✓ Tablo bulundu: {selector} ({len(table.find_all('tr'))} satır)")
                break
        
        if not table:
            logger.warning("⚠️ Sonuç tablosu bulunamadı")
            # Debug için sayfanın bir kısmını kaydet
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info("Debug için sayfa debug_page.html olarak kaydedildi")
            return []
        
        # Tablo satırlarını parse et
        rows = table.find_all('tr')
        
        # Header satırını atla
        header_found = False
        for row in rows:
            cells = row.find_all(['th', 'td'])
            
            # Header satırını tespit et
            if not header_found and cells and cells[0].name == 'th':
                header_found = True
                continue
            
            # Veri satırlarını işle
            if len(cells) < 2:
                continue
            
            # Her hücredeki veriyi çek
            row_data = {}
            
            for idx, cell in enumerate(cells):
                # Link varsa al
                link = cell.find('a')
                if link and link.get('href'):
                    href = link.get('href')
                    # Relative link'i absolute'a çevir
                    if not href.startswith('http'):
                        href = BASE_URL + (href if href.startswith('/') else '/' + href)
                    
                    row_data['baslik'] = link.get_text(strip=True)
                    row_data['link'] = href
                
                # Hücre içeriğini al
                text = cell.get_text(strip=True)
                if text:
                    # Kolon indexine göre isimlendir
                    if idx == 0:
                        row_data['sira'] = text
                    elif idx == 1 and 'baslik' not in row_data:
                        row_data['baslik'] = text
                    elif 'esas' in text.lower() or '/' in text:
                        row_data['esas_no'] = text
                    elif 'dönem' in text.lower() or 'yasama' in text.lower():
                        row_data['donem'] = text
                    elif any(durum in text.upper() for durum in ['KANUNLAŞTI', 'İŞLEMDE', 'KOMİSYONDA', 'GERİ ALINDI']):
                        row_data['durum'] = text
                    else:
                        # Genel field
                        row_data[f'field_{idx}'] = text
            
            # En azından başlık varsa ekle
            if row_data.get('baslik'):
                row_data['cekme_tarihi'] = datetime.now().isoformat()
                results.append(row_data)
                logger.debug(f"  ✓ Satır eklendi: {row_data.get('baslik', '')[:50]}")
        
        logger.info(f"✅ {len(results)} sonuç parse edildi")
        return results
        
    except Exception as e:
        logger.error(f"❌ Parse hatası: {e}")
        import traceback
        traceback.print_exc()
        return []


def handle_pagination() -> List[Dict[str, str]]:
    """
    Sayfalama varsa tüm sayfaları dolaşır ve sonuçları toplar
    """
    all_results = []
    page_num = 1
    
    while True:
        logger.info(f"📄 Sayfa {page_num} işleniyor...")
        
        # Mevcut sayfadaki sonuçları parse et
        results = parse_results_table()
        all_results.extend(results)
        
        if not results:
            logger.warning(f"⚠️ Sayfa {page_num}'de sonuç bulunamadı")
            break
        
        # Sonraki sayfa butonunu ara
        try:
            # Muhtemel pagination selectors
            next_button = None
            next_selectors = [
                "//a[contains(text(), 'Sonraki')]",
                "//a[contains(text(), 'İleri')]",
                "//a[contains(text(), '>')]",
                "//a[contains(@class, 'next')]",
                "//button[contains(text(), 'Sonraki')]",
                "//button[contains(@class, 'next')]",
                "//a[contains(@aria-label, 'Next')]",
            ]
            
            for selector in next_selectors:
                try:
                    next_button = driver.find_element(By.XPATH, selector)
                    # Disabled değilse
                    if 'disabled' not in next_button.get_attribute('class').lower():
                        break
                    else:
                        next_button = None
                except NoSuchElementException:
                    continue
            
            if next_button:
                logger.info(f"  ➡️  Sonraki sayfaya geçiliyor...")
                next_button.click()
                time.sleep(REQUEST_DELAY)
                wait_for_page_load()
                page_num += 1
            else:
                logger.info(f"✅ Tüm sayfalar tarandı (Toplam {page_num} sayfa)")
                break
                
        except Exception as e:
            logger.info(f"✅ Son sayfaya ulaşıldı: {e}")
            break
    
    return all_results


def save_to_json(data: List[Dict[str, str]], filename: str = OUTPUT_FILE):
    """Verileri JSON dosyasına kaydeder"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Veriler kaydedildi: {filename} ({len(data)} kayıt)")
    except Exception as e:
        logger.error(f"❌ JSON kaydetme hatası: {e}")
        raise


def main():
    """Ana scraper fonksiyonu"""
    logger.info("🚀 TBMM Kanun Teklifleri Sorgu Scraper başlatıldı")
    
    try:
        # 1. Veri dizinini oluştur
        create_data_directory()
        
        # 2. WebDriver'ı başlat
        driver = init_driver()
        
        # 3. Sorgu sayfasına git
        logger.info(f"🌐 Sorgu sayfası açılıyor: {SORGU_URL}")
        driver.get(SORGU_URL)
        wait_for_page_load()
        
        # Bot koruması varsa bekle
        time.sleep(5)
        
        # 4. Arama formunu doldur ve gönder
        # Burada parametreleri değiştirebilirsin
        success = fill_search_form(
            arama_kelime="",  # Boş = tüm sonuçlar
            donem="Son Dönem",  # veya "28.DÖNEM 3.Yasama Yılı" gibi
            durum=""  # Boş = tüm durumlar, veya "KANUNLAŞTI", "İŞLEMDE", vs.
        )
        
        if not success:
            logger.error("❌ Form gönderilemedi!")
            # Form bulunamadıysa, belki direkt sonuçlar sayfasındayız?
            logger.info("⚠️ Mevcut sayfadan sonuç çekmeye çalışılıyor...")
        
        # 5. Sonuçları çek (pagination dahil)
        results = handle_pagination()
        
        if not results:
            logger.warning("⚠️ Hiç sonuç bulunamadı!")
            save_to_json([])
            return
        
        # 6. Sonuçları kaydet
        save_to_json(results)
        
        logger.info(f"✅ Scraping tamamlandı! Toplam: {len(results)} kayıt")
        
        # Özet istatistik
        if results:
            logger.info("\n📊 İstatistikler:")
            logger.info(f"  • Toplam kayıt: {len(results)}")
            
            # Durum dağılımı
            durum_counts = {}
            for r in results:
                durum = r.get('durum', 'Bilinmiyor')
                durum_counts[durum] = durum_counts.get(durum, 0) + 1
            
            if durum_counts:
                logger.info("  • Durum dağılımı:")
                for durum, count in sorted(durum_counts.items(), key=lambda x: x[1], reverse=True):
                    logger.info(f"    - {durum}: {count}")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️ İşlem kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ Kritik hata: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Her durumda WebDriver'ı kapat
        close_driver()


if __name__ == "__main__":
    main()

