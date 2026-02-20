import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def get_chartink_data():
    url = "https://chartink.com/screener/stocks-10-range-2?export=csv"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code != 200:
            return []

        lines = response.text.splitlines()

        stocks = []

        # Skip header row
        for line in lines[1:]:
            parts = line.split(",")

            # NSE code usually in column index 2
            if len(parts) > 2:
                symbol = parts[2].strip()
                if symbol:
                    stocks.append(symbol)

        return stocks

    except Exception as e:
        return []


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)


def main():
    stocks = get_chartink_data()

    if stocks:
        message = "📊 Raxit AI - Chartink Scan Results\n\n"
        for i, stock in enumerate(stocks[:20], 1):
            message += f"{i}. {stock}\n"
        message += f"\nTotal Stocks: {len(stocks)}"
    else:
        message = "No valid stocks processed today."

    send_telegram(message)


if __name__ == "__main__":
    main()

