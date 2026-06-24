import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ==========================================
# IGN SYNDICATION HOOKS
# ==========================================
# Using the primary, ultra-stable Feedburner route for all categories
TARGET_FEED = "http://feeds.feedburner.com/ign/all.xml"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_notification(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram environment targets uninitialized. Check GitHub execution configurations.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print("IGN review metrics posted successfully!")
        else:
            print(f"Telegram Interface rejected deployment payload: {response.text}")
    except Exception as e:
        print(f"Failed dispatching to API pipeline endpoint: {e}")

def scrape_ign_reviews():
    print(f"Initializing IGN global extraction engine...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(TARGET_FEED, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Target syndicate endpoint down. Network code dropped: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('item')
        
        extracted_reviews = []
        
        for item in items:
            title = item.find('title').text.strip() if item.find('title') else "Unknown Review Title"
            
            # Filter Strategy: Ensure we are only picking items explicitly tagged as a "Review"
            if "review" not in title.lower():
                continue
                
            link = ""
            if item.find('link'):
                link = item.find('link').text.strip()
            
            description_tag = item.find('description') or item.find('summary')
            description = description_tag.text.strip() if description_tag else "No review summary payload available."
            # Strip internal tags and clamp text safely
            description = BeautifulSoup(description, "html.parser").text[:120].strip() + "..."
            
            # Clean video suffix injection
            video_link = link + "-video" if link and not link.endswith('/') else link
            
            extracted_reviews.append({
                "title": title,
                "summary": description,
                "url": link,
                "video": video_link
            })
            
            # Cap execution processing depth at the top 5 most recent reviews
            if len(extracted_reviews) >= 5:
                break
            
        if extracted_reviews:
            alert_payload = f"🎮 <b>IGN Top Multi-Category Review Metrics</b> 🎮\n"
            alert_payload += f"📅 Scrape Run: {datetime.today().strftime('%d-%b-%Y')}\n\n"
            
            for index, review in enumerate(extracted_reviews, 1):
                alert_payload += f"{index}. <b>{review['title']}</b>\n"
                alert_payload += f"📝 <i>{review['summary']}</i>\n"
                alert_payload += f"🔗 <a href=\"{review['url']}\">Read Review Text</a>\n"
                alert_payload += f"🎬 <a href=\"{review['video']}\">Watch Video Review</a>\n\n"
                
            send_telegram_notification(alert_payload)
        else:
            print("No matches tracked containing review tags during this feed cycle.")
            
    except Exception as e:
        print(f"Scraper core crashed: {e}")

if __name__ == "__main__":
    scrape_ign_reviews()
