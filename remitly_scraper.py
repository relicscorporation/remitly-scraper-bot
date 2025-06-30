import requests
import json
from datetime import datetime
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram error: {e}")

def scrape_remitly():
    try:
        # Placeholder scraping logic
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "from": "USD",
            "to": "INR",
            "rate": 83.45,
            "fee": 2.99,
            "mode": "Bank Deposit"
        }

        with open("output.json", "w") as f:
            json.dump(result, f, indent=2)

        print("Scraping success!")

    except Exception as e:
        send_telegram(f"❌ Remitly Scraper Error: {e}")
        raise

if __name__ == "__main__":
    scrape_remitly()
