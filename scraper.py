import os
import re
import sys
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

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
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload, timeout=12)
    except Exception as e:
        print(f"Telegram failed: {e}")

def run_scraper_cycle():
    print(f"Executing portal scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    consolidated_matches = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for name, endpoint in PORTALS.items():
        try:
            res = requests.get(endpoint, headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                for anchor in soup.find_all('a'):
                    text = anchor.get_text(strip=True)
                    href = anchor.get('href', '')
                    for pattern in HIGH_PAY_KEYWORDS:
                        if re.search(pattern, text, re.IGNORECASE):
                            link = href if href.startswith('http') else endpoint
                            consolidated_matches.append(f"💎 *{text}*\n📍 Link: {link}")
                            break
        except Exception as e:
            print(f"Skipping {name}: {e}")
            continue

    if consolidated_matches:
        alert_body = "🚀 *New Govt Tech Jobs Found!*\n\n" + "\n\n".join(consolidated_matches)
        send_telegram_alert(alert_body)
    else:
        send_telegram_alert("🔍 *Daily Scan Complete:* Checked portals via Indian cloud server. No new matches today.")

if __name__ == "__main__":
    # Startup verification alert
    send_telegram_alert("⚡ *Render Cloud Connected:* Automated background service initialized successfully.")
    
    # Persistent cloud execution engine loop
    while True:
        run_scraper_cycle()
        print("Sleeping for 24 hours until the next tracking run...")
        time.sleep(86400) # Wait exactly 24 hours
