import os
import re
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
    r"teacher", r"instructor", r"computer science"
]

def send_telegram_alert(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(telegram_url, json=payload, timeout=10)
        print(f"Telegram API Response Status: {response.status_code}")
    except Exception as e:
        print(f"Failed to send Telegram ping: {e}")

def run_pipeline():
    # --- HEARTBEAT PING (Verifies your setup works immediately) ---
    print("Sending connection test ping to Telegram...")
    send_telegram_alert("⚡ *Govt Job Monitor Link Active:* Script successfully initialized in the cloud. Beginning portal scans...")

    consolidated_matches = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for name, endpoint in PORTALS.items():
        try:
            print(f"Querying portal: {name}")
            res = requests.get(endpoint, headers=headers, timeout=15)
            print(f"Portal {name} responded with HTTP: {res.status_code}")
            
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

    # --- FINAL SCAN RESULTS ---
    if consolidated_matches:
        alert_body = "🚀 *New Govt Tech/Teaching Jobs Found!*\n\n" + "\n\n".join(consolidated_matches)
        send_telegram_alert(alert_body)
    else:
        send_telegram_alert("🔍 *Scan Finished:* Checked active endpoints. No new matching tech or teaching postings found right now.")

if __name__ == "__main__":
    run_pipeline()
