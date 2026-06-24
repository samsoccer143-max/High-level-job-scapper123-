import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID", "")).strip().replace('"', '').replace("'", "")

# Simplified list of portals known for structured tables
PORTALS = {
    "National Career Service": "https://betacloud.ncs.gov.in/latest-update",
    "CDAC Current Jobs": "https://www.cdac.in/index.aspx?id=current_jobs"
}

HIGH_PAY_KEYWORDS = [r"scientist", r"technical officer", r"programmer", r"system analyst", r"software engineer"]

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Telegram delivery failed: {e}")

def run_scraper_cycle():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    
    for name, endpoint in PORTALS.items():
        try:
            res = session.get(endpoint, timeout=20)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Target tables specifically
                for table in soup.find_all('table'):
                    for row in table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) > 2:
                            row_text = " ".join([c.get_text(strip=True) for c in cells]).lower()
                            
                            # Check if the row matches your tech criteria
                            if any(re.search(k, row_text) for k in HIGH_PAY_KEYWORDS):
                                # Extract data based on typical table columns
                                job_title = cells[0].get_text(strip=True)
                                pay_info = cells[1].get_text(strip=True)
                                date_info = cells[2].get_text(strip=True)
                                link = cells[0].find('a')['href'] if cells[0].find('a') else endpoint
                                
                                alert = (f"💎 <b>{job_title}</b>\n"
                                         f"💰 <i>Pay:</i> {pay_info}\n"
                                         f"📅 <i>Dates:</i> {date_info}\n"
                                         f"📍 <a href='{link}'>View Job</a>")
                                send_telegram_alert(alert)
        except Exception as e:
            print(f"Error parsing {name}: {e}")

if __name__ == "__main__":
    run_scraper_cycle()
