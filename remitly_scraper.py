import requests
import json
import csv
import os
from datetime import datetime

# Ambil token dari secret GitHub Actions
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN or CHAT_ID not found")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram error: {e}")

def save_to_csv(data, filename="output.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def scrape_remitly_real():
    url = "https://api.remitly.io/v3/calculator/estimate"
    params = {
        "conduit": "USA:USD-IND:INR",
        "anchor": "SEND",
        "amount": 100,
        "purpose": "OTHER",
        "customer_segment": "UNRECOGNIZED",
        "strict_promo": "false"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    data = r.json()

    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "from_currency": "USD",
        "to_currency": "INR",
        "send_amount": params["amount"],
        "fee": data.get("total_fee"),
        "delivery_amount": data.get("total_delivery_amount"),
        "exchange_rate": data.get("exchange_rate"),
        "method": data.get("delivery_method")
    }

    return result

if __name__ == "__main__":
    try:
        result = scrape_remitly_real()
        save_to_csv(result)
        send_telegram(
            f"✅ Remitly Scraper Success!\n💱 Rate: {result['exchange_rate']}\n📤 Fee: ${result['fee']}\n📥 Received: ₹{result['delivery_amount']}"
        )
        print("Scraping success!")

    except Exception as e:
        send_telegram(f"❌ Remitly Scraper Failed:\n{e}")
        raise
