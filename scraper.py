import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Load your secrets from GitHub Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID", "")).strip().replace('"', '').replace("'", "")

# Matrix of reliable National Govt Portals
PORTALS = {
    "National Career Service": "https://betacloud.ncs.gov.in/latest-update",
    "UPSC Notifications": "https://www.upsc.gov.in/whats-new",
    "SSC Notices": "https://ssc.gov.in/candidate-portal/notices",
    "Digital India Careers": "https://www.digitalindia.gov.in/opportunities",
    "CDAC Current Jobs": "https://www.cdac.in/index.aspx?id=current_jobs",
    "NIC Recruitment": "https://www.nic.in/recruitment/"
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
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Telegram delivery failed: {e}")

def run_scraper_cycle():
    print(f"Starting scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    consolidated_matches = []
    
    # Session setup to mimic human browser headers
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    for name, endpoint in PORTALS.items():
        try:
            res = session.get(endpoint, timeout=20)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Check for keywords in links and table data
                for element in soup.find_all(['a', 'td']):
                    text = element.get_text(strip=True)
                    href = element.get('href', '') if element.name == 'a' else endpoint
                    
                    for pattern in HIGH_PAY_KEYWORDS:
                        if re.search(pattern, text, re.IGNORECASE):
                            link = href if href.startswith('http') else endpoint
                            entry = f"💎 <b>{text}</b>\n📍 <a href='{link}'>Click here to view</a>"
                            if entry not in consolidated_matches:
                                consolidated_matches.append(entry)
                            break
        except Exception as e:
            print(f"Skipping {name} due to network restriction: {e}")

    if consolidated_matches:
        alert_body = "🚀 <b>New Tech Jobs Found!</b>\n\n" + "\n\n".join(consolidated_matches)
        send_telegram_alert(alert_body)
    else:
        # Optional: Send a 'no jobs' message or keep silent to save notifications
        print("No matches found in this cycle.")

if __name__ == "__main__":
    run_scraper_cycle()
