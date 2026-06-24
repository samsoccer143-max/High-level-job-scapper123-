import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID", "")).strip().replace('"', '').replace("'", "")

# Add more portals here. Structure: "Name": (URL, CSS_Selector_For_Rows)
PORTALS = {
    "NCS": ("https://betacloud.ncs.gov.in/latest-update", "tr"),
    "CDAC": ("https://www.cdac.in/index.aspx?id=current_jobs", "tr"),
    "NIC": ("https://www.nic.in/recruitment/", "div.rec-item"),
    "Digital India": ("https://www.digitalindia.gov.in/opportunities", "div.job-row")
}

HIGH_PAY_KEYWORDS = [r"scientist", r"technical officer", r"programmer", r"system analyst", r"software engineer"]

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Telegram error: {e}")

def run_scraper_cycle():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    
    print(f"--- Scan started at {datetime.now()} ---")
    
    for name, (url, selector) in PORTALS.items():
        try:
            res = session.get(url, timeout=20)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Find rows based on the specific CSS selector for that site
                for item in soup.select(selector):
                    text = item.get_text(" ", strip=True).lower()
                    
                    if any(re.search(k, text) for k in HIGH_PAY_KEYWORDS):
                        # Extracting a link
                        link = item.find('a')['href'] if item.find('a') else url
                        if not link.startswith('http'): link = "https://" + url.split('/')[2] + link
                        
                        alert = f"💎 <b>Match found on {name}!</b>\n\n{item.get_text(strip=True)[:200]}...\n📍 <a href='{link}'>View Details</a>"
                        send_telegram_alert(alert)
        except Exception as e:
            print(f"Failed to scan {name}: {e}")

if __name__ == "__main__":
    run_scraper_cycle()
