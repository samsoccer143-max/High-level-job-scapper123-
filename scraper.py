import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# ==========================================
# 1. USER USER CONFIGURATION (DOB: 1-May-1994)
# ==========================================
DOB = "1994-05-01"  
REQUIRED_EXP = 4    

# Target matching keywords for qualifications
QUALIFICATION_KEYWORDS = ["computer science", "cs", "it", "information technology", "b.tech", "m.tech", "mca", "software engineer"]

# High pay scale anchors (7th CPC Level 10+, Grade A/B, Bank Scale II/III/IV, Scientist C/D)
HIGH_PAY_KEYWORDS = [
    "level 10", "level 11", "level 12", "level 13", "level-10", "level-11", "level-12",
    "scientist c", "scientist d", "grade b", "scale ii", "scale iii", "scale iv", 
    "manager", "system analyst", "executive engineer", "ctc"
]

# Real, active public job feeds tracking Central Govt, State PSCs, Banks, and PSUs
PORTAL_FEEDS = [
    "https://www.sarkarinaukriblog.com/feeds/posts/default", # Core Atom Feed for UPSC/PSU/Central Jobs
    "https://www.sarkarinaukriblog.com/feeds/posts/default/-/Officer" # Specific Officer-level category filter
]

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def calculate_current_age(dob_str):
    """Dynamically calculates age based on the current date."""
    birth_date = datetime.strptime(dob_str, "%Y-%m-%d")
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def check_eligibility(title, content):
    """Filters data based on user qualification, high pay grade, and 4+ years of experience."""
    text_corpus = (title + " " + content).lower()
    
    # 1. Match Computer Science/IT Domain
    if not any(kw in text_corpus for kw in QUALIFICATION_KEYWORDS):
        return False
        
    # 2. Match High Pay Grade Markers
    if not any(kw in text_corpus for kw in HIGH_PAY_KEYWORDS):
        return False
        
    # 3. Match experience requirements (Scanning for keywords like '4 years', '4+ years', 'experience')
    # Since experience is critical, we check for presence of experience terms or explicit higher cadres like Scale II/III
    exp_indicators = ["experience", "years", "yrs", "scale ii", "scale iii", "scientist c"]
    if not any(indicator in text_corpus for indicator in exp_indicators):
        return False
        
    return True

def parse_age_limit(text_corpus):
    """Attempts to find stated maximum age limits via regex patterns."""
    age_match = re.search(r'(?:max(?:imum)?\s+age.*?|age\s+limit.*?|up\s+to\s+)(\d{2})', text_corpus, re.IGNORECASE)
    return int(age_match.group(1)) if age_match else None

def send_telegram_notification(message):
    """Dispatches formatted message chunk via Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram configuration missing. Check your GitHub Secrets setup.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print("Telegram alert pushed successfully!")
        else:
            print(f"Telegram error: {response.text}")
    except Exception as e:
        print(f"Failed sending Telegram alert: {e}")

def run_screener():
    current_age = calculate_current_age(DOB)
    print(f"Starting Scraper. Calculated Age: {current_age} (DOB: {DOB})")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    eligible_jobs = []
    seen_links = set() # Avoid duplication across feeds
    
    for feed_url in PORTAL_FEEDS:
        try:
            print(f"Fetching updates from live portal feed: {feed_url}")
            response = requests.get(feed_url, headers=headers, timeout=20)
            if response.status_code != 200:
                continue
                
            # Parse Atom/XML framework
            soup = BeautifulSoup(response.content, 'xml')
            entries = soup.find_all('entry') or soup.find_all('item')
            
            for entry in entries:
                title = entry.find('title').text.strip() if entry.find('title') else ""
                
                # Fetch target web link
                link_tag = entry.find('link')
                link = ""
                if link_tag:
                    link = link_tag.get('href') or link_tag.text.strip()
                
                if not link or link in seen_links:
                    continue
                    
                # Content/Summary description block
                content_tag = entry.find('content') or entry.find('description') or entry.find('summary')
                content = content_tag.text.strip() if content_tag else ""
                
                # Verify background eligibility rule matrices
                if check_eligibility(title, content):
                    max_age = parse_age_limit(content)
                    
                    # Age safety check gate 
                    if max_age and current_age > max_age:
                        print(f"Skipped: {title} (Age limit {max_age} exceeded current age {current_age})")
                        continue
                        
                    seen_links.add(link)
                    eligible_jobs.append({
                        "title": title,
                        "link": link,
                        "max_age": max_age or "Not specified (Check link)"
                    })
                    
        except Exception as e:
            print(f"Error accessing feed {feed_url}: {e}")

    # Process and build notification string
    if eligible_jobs:
        alert_body = f"🚨 *High-Pay Govt Jobs Matching Your Profile!* 🚨\n"
        alert_body += f"👤 Your Calculated Age: {current_age} years\n"
        alert_body += f"📅 Checked On: {datetime.today().strftime('%d-%b-%Y')}\n\n"
        
        for index, job in enumerate(eligible_jobs, 1):
            alert_body += f"{index}. *{job['title']}*\n"
            alert_body += f"   Target Age Bracket Max: {job['max_age']}\n"
            alert_body += f"   🔗 [View Details & Apply Here]({job['link']})\n\n"
            
        send_telegram_notification(alert_body)
    else:
        print("No matches tracked during today's update cycle.")

if __name__ == "__main__":
    run_screener()
