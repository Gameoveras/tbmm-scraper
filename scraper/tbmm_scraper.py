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

import requests
from bs4 import BeautifulSoup

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%i:%S'
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

# User-Agent header
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}


def create_data_directory():
    """Veri dizinini oluşturur"""
    os.makedirs(DATA_DIR, exist_ok=True)
    logger.info(f"✅ Veri dizini hazır: {DATA_DIR}")


def fetch_page(url: str, retries: int = MAX_RETRIES) -> Optional[str]:
    """Belirtilen URL'den HTML içeriğini çeker"""
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"🌐 Sayfa çekiliyor: {url} (Deneme {attempt}/{retries})")
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            response.encoding = 'utf-8'
            logger.info(f"✅ Sayfa başarıyla çekildi ({len(response.text)} karakter)")
            return response.text
        except requests.RequestException as e:
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
    
    # Teklif linklerini bul
    # TBMM sitesinde genellikle .kanunTeklifiListesi veya benzeri class kullanılır
    # Eğer yapı değişirse bu selector'ı güncellemeniz gerekir
    links = soup.select('a[href*="kanun"]')  # Genel bir selector
    
    if not links:
        # Alternatif: tüm linkleri tara ve "teklif" içerenleri al
        all_links = soup.find_all('a', href=True)
        links = [link for link in all_links if 'teklif' in link.get('href', '').lower()]
    
    logger.info(f"📋 {len(links)} adet teklif linki bulundu")
    
    seen_urls = set()
    for link in links:
        href = link.get('href', '')
        if not href or href in seen_urls:
            continue
        
        full_url = urljoin(BASE_URL, href)
        title = link.get_text(strip=True)
        
        if title and full_url not in seen_urls:
            proposals_list.append({
                'baslik': title,
                'link': full_url
            })
            seen_urls.add(full_url)
    
    logger.info(f"✅ {len(proposals_list)} benzersiz teklif belirlendi")
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
    
    # İçerik alanını bul (TBMM sitesinde genellikle #icerik id'si kullanılır)
    content_div = soup.select_one('#icerik, .icerik, .kanunMetni, .teklif-metni, main, article')
    
    if content_div:
        # Script ve style etiketlerini temizle
        for tag in content_div.find_all(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        full_text = content_div.get_text(separator='\n', strip=True)
        
        # Esas No ve Dönem/Yasama bilgisini çıkar
        esas_no = extract_esas_no(full_text)
        donem_yasama = extract_donem_yasama(full_text)
        
        proposal['metin'] = full_text
        proposal['esasNo'] = esas_no
        proposal['donemYasamaYili'] = donem_yasama
        
        logger.info(f"✅ İçerik çekildi ({len(full_text)} karakter)")
    else:
        logger.warning(f"⚠️ İçerik alanı bulunamadı: {url}")
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


if __name__ == "__main__":
    main()

