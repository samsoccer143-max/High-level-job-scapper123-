import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# 1. User Profile Configuration
DOB = "1994-05-01"  
REQUIRED_EXP = 4    
QUALIFICATION_KEYWORDS = ["computer science", "cs", "it", "information technology", "b.tech", "m.tech", "mca"]
HIGH_PAY_KEYWORDS = ["level 10", "level 11", "level 12", "level 13", "grade a", "scale ii", "scale iii", "ctc", "scientist c", "scientist d"]

# Fetch Telegram Credentials from GitHub Secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def calculate_current_age(dob_str):
    birth_date = datetime.strptime(dob_str, "%Y-%m-%d")
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def check_eligibility(job_title, job_description, max_age_limit):
    current_age = calculate_current_age(DOB)
    content_lower = (job_title + " " + job_description).lower()
    
    if max_age_limit and current_age > max_age_limit:
        return False
    if not any(keyword in content_lower for keyword in QUALIFICATION_KEYWORDS):
        return False
    if not any(keyword in content_lower for keyword in HIGH_PAY_KEYWORDS):
        return False
        
    return True

def send_telegram_notification(message):
    """Sends a formatted alert to your Telegram channel/chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram tokens are missing. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Telegram notification sent successfully!")
        else:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")

def fetch_and_filter_jobs(target_url):
    current_age = calculate_current_age(DOB)
    print(f"Running automated check... Current Age: {current_age}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(target_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Portal unreachable. Status: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        job_listings = soup.find_all('div', class_='job-item') # Placeholder template tag
        
        eligible_jobs = []

        for job in job_listings:
            title = job.find('h2').text.strip() if job.find('h2') else "Unknown Title"
            description = job.find('div', class_='description').text.strip() if job.find('div', class_='description') else ""
            link = job.find('a')['href'] if job.find('a') else "#"
            
            age_match = re.search(r'(?:max(?:imum)?\s+age.*?|age\s+limit.*?|up\s+to\s+)(\d{2})', description, re.IGNORECASE)
            max_age_limit = int(age_match.group(1)) if age_match else 35 
            
            if check_eligibility(title, description, max_age_limit):
                eligible_jobs.append({"title": title, "link": link, "max_age": max_age_limit})
                
        # If matches are found, compile and send a Telegram alert
        if eligible_jobs:
            alert_message = f"🚨 *New High-Pay Govt CS Jobs Found!* 🚨\n"
            alert_message += f"📅 Date: {datetime.today().strftime('%Y-%m-%d')}\n"
            alert_message += f"👤 Your Current Age: {current_age}\n\n"
            
            for index, job in enumerate(eligible_jobs, 1):
                alert_message += f"{index}. *{job['title']}*\n"
                alert_message += f"   Max Age Limit: {job['max_age']}\n"
                alert_message += f"   🔗 [Apply Here]({job['link']})\n\n"
                
            send_telegram_notification(alert_message)
        else:
            print("No new matching jobs found today.")
            
    except Exception as e:
        print(f"Scraper execution error: {e}")

if __name__ == "__main__":
    # URL configurations
    TARGET_PORTAL_URL = "https://example-govt-jobs-portal.gov.in/notifications" 
    fetch_and_filter_jobs(TARGET_PORTAL_URL)
