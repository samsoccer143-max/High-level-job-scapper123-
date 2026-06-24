@@ -4,52 +4,87 @@
from bs4 import BeautifulSoup
from datetime import datetime

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID", "")).strip().replace('"', '').replace("'", "")

# Add more portals here. Structure: "Name": (URL, CSS_Selector_For_Rows)
# --- ALL MAJOR GOVT PORTALS TRACKING MATRIX ---
PORTALS = {
    "NCS": ("https://betacloud.ncs.gov.in/latest-update", "tr"),
    "CDAC": ("https://www.cdac.in/index.aspx?id=current_jobs", "tr"),
    "NIC": ("https://www.nic.in/recruitment/", "div.rec-item"),
    "Digital India": ("https://www.digitalindia.gov.in/opportunities", "div.job-row")
    "National Career Service (NCS)": "https://betacloud.ncs.gov.in/latest-update",
    "Andaman eRecruitment Portal": "https://erecruitment.andamannicobar.gov.in/",
    "UPSC Current Openings": "https://www.upsc.gov.in/whats-new",
    "SSC Recruitment Notifications": "https://ssc.gov.in/candidate-portal/notices",
    "Digital India Careers": "https://www.digitalindia.gov.in/opportunities",
    "CDAC Tech Openings": "https://www.cdac.in/index.aspx?id=current_jobs",
    "NIC (National Informatics Centre)": "https://www.nic.in/recruitment/"
}

HIGH_PAY_KEYWORDS = [r"scientist", r"technical officer", r"programmer", r"system analyst", r"software engineer"]
# Your exact high-pay tech matrix keywords
HIGH_PAY_KEYWORDS = [
    r"scientist\s*[b-d]", r"technical\s*officer", r"programmer", 
    r"system\s*analyst", r"software\s*engineer", r"it\s*officer",
    r"computer science"
]

def send_telegram_alert(message):
    print("Routing message dispatch via open GitHub tunnel...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        requests.post(url, json=payload, timeout=15)
        res = requests.post(url, json=payload, timeout=15)
        print(f"Telegram API Response Status Code: {res.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")
        print(f"Network processing exception: {e}")

def run_scraper_cycle():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    print(f"Execution window opened at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    consolidated_matches = []

    print(f"--- Scan started at {datetime.now()} ---")
    # Persistent session with browser identity masking
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    })

    for name, (url, selector) in PORTALS.items():
    for name, endpoint in PORTALS.items():
        print(f"Querying portal: {name}")
        try:
            res = session.get(url, timeout=20)
            res = session.get(endpoint, timeout=20, allow_redirects=True)
            print(f"Portal {name} responded with HTTP: {res.status_code}")
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Find rows based on the specific CSS selector for that site
                for item in soup.select(selector):
                    text = item.get_text(" ", strip=True).lower()
                # Check both hyperlinked text and general table cells for keyword matches
                for element in soup.find_all(['a', 'td', 'li']):
                    text = element.get_text(strip=True)
                    href = element.get('href', '') if element.name == 'a' else ''

                    if any(re.search(k, text) for k in HIGH_PAY_KEYWORDS):
                        # Extracting a link
                        link = item.find('a')['href'] if item.find('a') else url
                        if not link.startswith('http'): link = "https://" + url.split('/')[2] + link
                        
                        alert = f"💎 <b>Match found on {name}!</b>\n\n{item.get_text(strip=True)[:200]}...\n📍 <a href='{link}'>View Details</a>"
                        send_telegram_alert(alert)
                    for pattern in HIGH_PAY_KEYWORDS:
                        if re.search(pattern, text, re.IGNORECASE):
                            link = href if href.startswith('http') else endpoint
                            match_entry = f"💎 <b>{text}</b>\n🏛️ <i>Source: {name}</i>\n📍 Link: {link}"
                            if match_entry not in consolidated_matches:
                                consolidated_matches.append(match_entry)
                            break
        except Exception as e:
            print(f"Failed to scan {name}: {e}")
            print(f"Network restriction or block on {name}: {e}")
            continue

    if consolidated_matches:
        # Group into clean readable sections if multiple jobs are found
        alert_body = "🚀 <b>New Govt Tech Jobs Found!</b>\n\n" + "\n\n---\n\n".join(consolidated_matches)
        send_telegram_alert(alert_body)
    else:
        send_telegram_alert("🔍 <b>Daily Scan Complete:</b> Checked all central & local govt portals. No new job postings match your tech matrix today.")

if __name__ == "__main__":
    run_scraper_cycle()
