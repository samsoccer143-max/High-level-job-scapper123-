import os
import re
import requests
from bs4 import BeautifulSoup

# --- PULL IN KEYS FROM SECURE GITHUB VAULT ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

PORTALS = {
    "National Career Service": "https://betacloud.ncs.gov.in/latest-update",
    "National Informatics Centre": "https://recruitment.nic.in/"
}

HIGH_PAY_KEYWORDS = [
    r"scientist\s*[b-d]", r"technical\s*officer", r"programmer", 
    r"system\s*analyst", r"software\s*engineer", r"it\s*officer"
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
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for name, endpoint in PORTALS.items():
        try:
            res = requests.get(endpoint, headers=headers, timeout=12)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                for anchor in soup.find_all('a'):
                    text = anchor.get_text(strip=True)
                    href = anchor.get('href', '')
                    
                    for pattern in HIGH_PAY_KEYWORDS:
                        if re.search(pattern, text, re.IGNORECASE):
                            consolidated_matches.append(f"💎 *{text}*\n📍 Link: {href if href.startswith('http') else endpoint}")
                            break
        except Exception as e:
            print(f"Skipping {name} due to an error: {e}")
            continue

    # --- UPDATED NOTIFICATION LOGIC ---
    if consolidated_matches:
        alert_body = "🚀 *New High-Pay Govt Tech Jobs Found!*\n\n" + "\n\n".join(consolidated_matches)
        send_telegram_alert(alert_body)
    else:
        # This will send a message to your phone even if nothing was found
        send_telegram_alert("🔍 *Daily Scan Complete:* No new high-paying tech roles posted on the portals today.")

if __name__ == "__main__":
    run_pipeline()
