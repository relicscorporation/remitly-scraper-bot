import sys
import os
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright

# === Konfigurasi Telegram ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN or CHAT_ID not found")
        return
    try:
        import requests
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

def scrape_transfer(from_country="GBR", to_country="IND"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=".auth/remitly.json")
        page = context.new_page()

        print(f"🌍 Setting FROM {from_country} TO {to_country}...")

        # Step 1: Open profile & ganti negara
        page.goto("https://www.remitly.com/gb/en/users/settings/profile", timeout=60000)
        page.click('button:has-text("Edit")')
        page.select_option('[data-testid="source-country"]', from_country)
        page.select_option('[data-testid="destination-country"]', to_country)
        page.click('button:has-text("Save")')
        page.wait_for_timeout(4000)  # kasih waktu update

        # Step 2: Buka halaman transfer/send
        page.goto("https://www.remitly.com/gb/en/transfer/send", timeout=60000)
        page.wait_for_selector('[data-testid="recipient-amount"]')

        send_amount = float(page.locator('[data-testid="send-amount-input"]').input_value())
        recv_text = page.locator('[data-testid="recipient-amount"]').inner_text()
        recv_amount = float(recv_text.replace("₹", "").replace(",", "").strip())

        method = page.locator('[data-testid="delivery-method-description"]').inner_text()
        fee_text = page.locator('[data-testid="transfer-fee-amount"]').inner_text()
        fee = float(fee_text.replace("£", "").replace(",", "").strip())

        rate = round(recv_amount / send_amount, 4)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "from_country": from_country,
            "to_country": to_country,
            "send_amount": send_amount,
            "delivery_amount": recv_amount,
            "exchange_rate": rate,
            "fee": fee,
            "method": method
        }

        browser.close()
        return result

# ========== Main Run ==========
if __name__ == "__main__":
    from_country = sys.argv[1] if len(sys.argv) > 1 else "GBR"
    try:
        result = scrape_transfer(from_country)
        save_to_csv(result)
        send_telegram(
            f"✅ Remitly Scrape Success!\n🌍 From: {from_country} → IND\n💱 Rate: {result['exchange_rate']}\n💸 Fee: £{result['fee']}\n📥 Received: ₹{result['delivery_amount']}\n🏦 Method: {result['method']}"
        )
        print("✅ Success")
    except Exception as e:
        send_telegram(f"❌ Remitly Scrape Failed ({from_country}):\n{e}")
        raise
