import requests
import os
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def get_chartink_data():
    url = "https://chartink.com/screener/stocks-10-range-2"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    with requests.Session() as s:
        # Step 1: Get page and CSRF token
        r = s.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        token_tag = soup.find("meta", {"name": "csrf-token"})
        if not token_tag:
            return []

        token = token_tag["content"]

        s.headers.update({
            "X-CSRF-TOKEN": token,
            "User-Agent": "Mozilla/5.0",
            "Referer": url
        })

        # Step 2: Extract scan_clause
        scan_input = soup.find("input", {"name": "scan_clause"})
        if not scan_input:
            return []

        scan_clause = scan_input["value"]

        payload = {
            "scan_clause": scan_clause
        }

        # Step 3: Post request to get results
        response = s.post(
            "https://chartink.com/screener/process",
            data=payload
        )

        if response.status_code != 200:
            return []

        data = response.json()

        stocks = []

        if "data" in data:
            for stock in data["data"]:
                stocks.append(stock.get("nsecode", ""))

        return stocks


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
    else:
        message = "No valid stocks processed today."

    send_telegram(message)


if __name__ == "__main__":
    main()


