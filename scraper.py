import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID", "")).strip().replace('"', '').replace("'", "")

PORTALS = {
    "National Career Service (NCS)": "https://betacloud.ncs.gov.in/latest-update",
    "Andaman eRecruitment Portal": "https://erecruitment.andamannicobar.gov.in/"
}

HIGH_PAY_KEYWORDS = [
    r"scientist\s*[b-d]", r"technical\s*officer", r"programmer", 
    r"system\s*analyst", r"software\s*engineer", r"it\s*officer",
    r"computer science"
]

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        print(f"Telegram Delivery Status: {res.status_code}")
    except Exception as e:
        print(f"Telegram network issue: {e}")

def run_scraper_cycle():
    print(f"Launching secure bypass scraper window at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    consolidated_matches = []
    
    # --- STEALTH HEADERS SET: Mimics a real Windows 10 Chrome Browser ---
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })
    
    for name, endpoint in PORTALS.items():
        print(f"Connecting to: {name}...")
        try:
            # Added an allow_redirects=True to handle internal server routing shifts safely
            res = session.get(endpoint, timeout=20, allow_redirects=True)
            print(f"Portal {name} responded with Code: {res.status_code}")
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                for anchor in soup.find_all('a'):
                    text = anchor.get_text(strip=True)
                    href = anchor.get('href', '')
                    
                    for pattern in HIGH_PAY_KEYWORDS:
                        if re.search(pattern, text, re.IGNORECASE):
                            link = href if href.startswith('http') else endpoint
                            consolidated_matches.append(f"<b>💎 {text}</b>\n📍 Link: {link}")
                            break
            else:
                print(f"⚠️ Access denied by firewall rules on {name} (Status Code: {res.status_code})")
                
        except Exception as e:
            print(f"Failed to scan {name} due to network wall: {e}")
            continue

    if consolidated_matches:
        alert_body = "🚀 <b>New Govt Tech Jobs Found!</b>\n\n" + "\n\n".join(consolidated_matches)
        send_telegram_alert(alert_body)
    else:
        send_telegram_alert("🔍 <b>Daily Scan Complete:</b> Checked portals successfully. No new matching job configurations found today.")

if __name__ == "__main__":
    run_scraper_cycle()
