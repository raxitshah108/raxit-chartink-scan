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
        r = s.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        token = soup.find("meta", {"name": "csrf-token"})["content"]
        s.headers.update({
            "X-CSRF-TOKEN": token,
            "User-Agent": "Mozilla/5.0",
            "Referer": url
        })

        scan_clause = soup.find("input", {"name": "scan_clause"})["value"]

        payload = {
            "scan_clause": scan_clause
        }

        response = s.post(
            "https://chartink.com/screener/process",
            data=payload
        )

        data = response.json()

        stocks = []

        if "data" in data:
            for stock in data["data"]:
                stocks.append(stock["nsecode"])

        return stocks


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "ch

