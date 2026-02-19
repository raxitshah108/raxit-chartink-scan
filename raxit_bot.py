import requests
import os
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_chartink_data():
    url = "https://chartink.com/screener/stocks-10-range-2"
    
    with requests.Session() as s:
        r = s.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        
        token = soup.find("meta", {"name": "csrf-token"})["content"]
        s.headers["X-CSRF-TOKEN"] = token
        
        payload = {
            "scan_clause": ""
        }
        
        data = s.post("https://chartink.com/screener/process", data=payload).json()
        
        stocks = []
        for stock in data["data"]:
            stocks.append(stock["nsecode"])
        
        return stocks

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

def main():
    stocks = get_chartink_data()
    
    if stocks:
        msg = "📊 Chartink Scan Results:\n\n"
        for i, stock in enumerate(stocks[:20], 1):
            msg += f"{i}. {stock}\n"
    else:
        msg = "No valid stocks today."
    
    send_telegram(msg)

if __name__ == "__main__":
    main()
