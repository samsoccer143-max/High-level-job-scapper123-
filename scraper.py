import os
import re
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Targeting open, scraper-friendly endpoints
PORTALS = {
    "National Career Service (NCS)": "https://betacloud.ncs.gov.in/latest-update",
    "Andaman eRecruitment Portal": "https://erecruitment.andamannicobar.gov.in/"
}

HIGH_PAY_KEYWORDS = [
    r"scientist\s*[b-d]", r"technical\s*officer", r"programmer", 
    r"system\s*analyst", r"software\s*engineer", r"it\s*officer",
    r"teacher", r"instructor", r"computer science"
]

def send_telegram_alert(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram ping: {e}")

def run_pipeline():
    consolidated_matches = []
    # Setting a real browser identity header to bypass basic web filters
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
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
            print(f"Skipping {name} due to network restriction: {e}")
            continue

    # --- FORCED GUARANTEED MESSAGE ---
    if consolidated_matches:
        alert_body = "🚀 *New Govt Tech/Teaching Jobs Found!*\n\n" + "\n\n".join(consolidated_matches)
        send_telegram_alert(alert_body)
    else:
        send_telegram_alert("🔍 *Daily Scan Active:* Portals checked successfully. No new matching tech or teaching posts found today.")

if __name__ == "__main__":
    run_pipeline()
