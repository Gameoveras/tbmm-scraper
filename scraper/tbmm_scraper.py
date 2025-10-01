#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TBMM Kanun Teklifleri Scraper
Bu script TBMM web sitesinden kanun tekliflerini çeker ve JSON formatında kaydeder.
"""

import os
import re
import json
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
LIST_URL = f"{BASE_URL}/Yasama/KanunTeklifi"
DATA_DIR = "data"
OUTPUT_FILE = f"{DATA_DIR}/proposals.json"
REQUEST_DELAY = 2  # Saniye cinsinden bekleme süresi
MAX_RETRIES = 3
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
    chrome_options.add_argument('--headless')  # Tarayıcı gösterilmez
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
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


def fetch_page(url: str, retries: int = MAX_RETRIES) -> Optional[str]:
    """Belirtilen URL'den HTML içeriğini çeker (Selenium ile)"""
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"🌐 Sayfa çekiliyor: {url} (Deneme {attempt}/{retries})")
            
            driver = init_driver()
            driver.get(url)
            
            # JavaScript'in yüklenmesi için bekle
            logger.info("⏳ JavaScript yüklenene kadar bekleniyor...")
            time.sleep(5)  # Bot korumasının geçmesi için bekle
            
            # Sayfanın body elementinin yüklenmesini bekle
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Sayfa tamamen yüklendikten sonra HTML'i al
            html = driver.page_source
            
            logger.info(f"✅ Sayfa başarıyla çekildi ({len(html)} karakter)")
            
            # Hala bot koruması var mı kontrol et
            if len(html) < 10000 or 'challenge' in html.lower():
                logger.warning("⚠️ Bot koruması aktif olabilir, biraz daha bekleniyor...")
                time.sleep(5)
                html = driver.page_source
            
            return html
            
        except Exception as e:
            logger.warning(f"⚠️ Hata (Deneme {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(REQUEST_DELAY * 2)
            else:
                logger.error(f"❌ Sayfa çekilemedi: {url}")
                return None
    return None


def extract_esas_no(text: str) -> str:
    """Metin içinden Esas No'yu çıkarır"""
    # Örnek: "Esas No: 2/1234" veya "(2/1234)"
    pattern = r'(?:Esas\s*No[:\s]+)?(\d+/\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else ''


def extract_donem_yasama(text: str) -> str:
    """Metin içinden Dönem/Yasama Yılı bilgisini çıkarır"""
    # Örnek: "28. Dönem 2. Yasama Yılı"
    pattern = r'(\d+)\.\s*Dönem\s+(\d+)\.\s*Yasama\s+Yılı'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return ''


def scrape_proposal_list() -> List[Dict[str, str]]:
    """Ana liste sayfasından teklif linklerini çeker"""
    html = fetch_page(LIST_URL)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    proposals_list = []
    
    # TBMM sitesinin farklı olası yapılarını dene
    # Önce spesifik selector'ları dene
    links = []
    
    # Seçenek 1: Liste sayfasındaki table veya ul içindeki linkler
    content_area = soup.select_one('.icerikMetni, .liste, .kanunListesi, #icerik, main')
    if content_area:
        links = content_area.find_all('a', href=True)
        logger.info(f"🔍 İçerik alanında {len(links)} link bulundu")
    
    # Seçenek 2: Tüm sayfada kanun teklifi linklerini ara
    if not links:
        all_links = soup.find_all('a', href=True)
        # Detay sayfalarına giden linkleri filtrele
        links = [
            link for link in all_links 
            if any(keyword in str(link.get('href', '')).lower() 
                   for keyword in ['kanunteklifi', 'kanun_teklifi', 'teklif', '/yasa', '/kt'])
        ]
        logger.info(f"🔍 Tüm sayfada {len(links)} potansiyel teklif linki bulundu")
    
    # Seçenek 3: Eğer hiç link bulamadıysak, table row'ları kontrol et
    if not links:
        table_rows = soup.select('table tr td a')
        links = [link for link in table_rows if link.get('href')]
        logger.info(f"🔍 Tablolarda {len(links)} link bulundu")
    
    logger.info(f"📋 Toplam {len(links)} adet link işlenecek")
    
    seen_urls = set()
    for link in links:
        href = link.get('href', '')
        if not href or href in seen_urls or href == '#':
            continue
        
        # JavaScript veya anchor linklerini atla
        if href.startswith('javascript:') or href.startswith('#'):
            continue
        
        full_url = urljoin(BASE_URL, href)
        title = link.get_text(strip=True)
        
        # Başlık yoksa veya çok kısaysa atla
        if not title or len(title) < 10:
            continue
        
        # Aynı URL'yi bir kez ekle
        if full_url not in seen_urls:
            proposals_list.append({
                'baslik': title,
                'link': full_url
            })
            seen_urls.add(full_url)
            logger.debug(f"  ✓ Eklendi: {title[:50]}...")
    
    logger.info(f"✅ {len(proposals_list)} benzersiz teklif belirlendi")
    
    # Debug için: Eğer hiç teklif bulunamadıysa, sayfanın bir kısmını logla
    if not proposals_list:
        logger.error("❌ Hiç teklif bulunamadı! Sayfa yapısı:")
        logger.error(f"Sayfa başlığı: {soup.title.string if soup.title else 'Yok'}")
        logger.error(f"İçerik uzunluğu: {len(html)} karakter")
        # İlk 500 karakteri logla
        logger.error(f"Sayfa önizleme: {html[:500]}")
    
    return proposals_list


def scrape_proposal_detail(proposal: Dict[str, str]) -> Dict[str, str]:
    """Bir teklifin detay sayfasını çeker ve içeriği parse eder"""
    url = proposal['link']
    logger.info(f"📄 Detay çekiliyor: {proposal['baslik'][:50]}...")
    
    html = fetch_page(url)
    if not html:
        logger.warning(f"⚠️ Detay sayfası çekilemedi, atlanıyor: {url}")
        return proposal
    
    soup = BeautifulSoup(html, 'lxml')
    
    # İçerik alanını bul - Birden fazla selector dene
    content_div = None
    selectors = [
        '#icerik',           # Genel içerik id'si
        '.icerik',           # Genel içerik class'ı
        '.icerikMetni',      # İçerik metni class'ı
        '.kanunMetni',       # Kanun metni özel class'ı
        '.teklif-metni',     # Teklif metni
        'main',              # HTML5 main elementi
        'article',           # HTML5 article elementi
        '.content',          # Genel content class'ı
        '#content',          # Genel content id'si
    ]
    
    for selector in selectors:
        content_div = soup.select_one(selector)
        if content_div:
            logger.debug(f"  İçerik bulundu: {selector}")
            break
    
    # Eğer hiçbir selector çalışmadıysa, body'yi kullan
    if not content_div:
        content_div = soup.find('body')
        if content_div:
            logger.warning(f"⚠️ Özel selector bulunamadı, body kullanılıyor")
    
    if content_div:
        # Script ve style etiketlerini temizle
        for tag in content_div.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        full_text = content_div.get_text(separator='\n', strip=True)
        
        # Boş veya çok kısa ise uyar
        if len(full_text) < 100:
            logger.warning(f"⚠️ İçerik çok kısa ({len(full_text)} karakter): {url}")
            logger.warning(f"İçerik önizleme: {full_text[:200]}")
        
        # Esas No ve Dönem/Yasama bilgisini çıkar
        esas_no = extract_esas_no(full_text)
        donem_yasama = extract_donem_yasama(full_text)
        
        proposal['metin'] = full_text
        proposal['esasNo'] = esas_no if esas_no else 'UNKNOWN'
        proposal['donemYasamaYili'] = donem_yasama if donem_yasama else 'UNKNOWN'
        
        logger.info(f"✅ İçerik çekildi ({len(full_text)} karakter, Esas: {esas_no}, Dönem: {donem_yasama})")
    else:
        logger.error(f"❌ Hiçbir içerik alanı bulunamadı: {url}")
        proposal['metin'] = ''
        proposal['esasNo'] = ''
        proposal['donemYasamaYili'] = ''
    
    # Rate limiting için bekle
    time.sleep(REQUEST_DELAY)
    
    return proposal


def save_to_json(proposals: List[Dict[str, str]]):
    """Teklifleri JSON dosyasına kaydeder"""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(proposals, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Veriler kaydedildi: {OUTPUT_FILE} ({len(proposals)} teklif)")
    except Exception as e:
        logger.error(f"❌ JSON kaydetme hatası: {e}")
        raise


def main():
    """Ana scraper fonksiyonu"""
    logger.info("🚀 TBMM Scraper başlatıldı")
    
    try:
        # 1. Veri dizinini oluştur
        create_data_directory()
        
        # 2. Liste sayfasını çek
        proposals = scrape_proposal_list()
        
        if not proposals:
            logger.warning("⚠️ Hiç teklif bulunamadı!")
            # Boş array kaydet
            save_to_json([])
            return
        
        # 3. Her teklifin detayını çek (ilk 20 teklif ile sınırlı - test için)
        # Üretimde bu limiti kaldırabilir veya artırabilirsiniz
        MAX_PROPOSALS = int(os.getenv('MAX_PROPOSALS', '20'))
        proposals_to_scrape = proposals[:MAX_PROPOSALS]
        
        logger.info(f"🔍 {len(proposals_to_scrape)} teklifin detayı çekilecek")
        
        detailed_proposals = []
        for i, proposal in enumerate(proposals_to_scrape, 1):
            logger.info(f"📊 İlerleme: {i}/{len(proposals_to_scrape)}")
            detailed = scrape_proposal_detail(proposal)
            
            # Sadece geçerli içeriğe sahip teklifleri kaydet
            if detailed.get('metin'):
                detailed_proposals.append(detailed)
        
        # 4. JSON'a kaydet
        save_to_json(detailed_proposals)
        
        logger.info(f"✅ Scraping tamamlandı! Toplam: {len(detailed_proposals)} teklif")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️ İşlem kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ Kritik hata: {e}", exc_info=True)
        raise
    finally:
        # Her durumda WebDriver'ı kapat
        close_driver()


if __name__ == "__main__":
    main()

