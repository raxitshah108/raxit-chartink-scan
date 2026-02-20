import os
import requests
import pandas as pd
import yfinance as yf

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "SBIN.NS", "LT.NS", "ITC.NS",
    "KOTAKBANK.NS", "AXISBANK.NS", "HCLTECH.NS",
    "MARUTI.NS", "BAJFINANCE.NS", "BHARTIARTL.NS",
    "ASIANPAINT.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS",
    "TITAN.NS", "NESTLEIND.NS", "ADANIENT.NS"
]



def check_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)

        # --- PRICE DATA (1 year)
        hist = ticker.history(period="1y")

        if hist.empty:
            return None

        latest_close = hist["Close"].iloc[-1]
        high_52 = hist["High"].max()

        # Condition 1: Near 52-week high (within 3%)
        if latest_close < 0.95 * high_52:
            return symbol.replace(".NS", "")

        return None

    except:
        return None

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
    tech_list = []
    growth_list = []
    final_list = []
    
    stocks = STOCKS
    
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            hist = ticker.history(period="1y")

            if hist.empty:
                continue

            latest_close = hist["Close"].iloc[-1]
            high_52 = hist["High"].max()

            if latest_close >= 0.95 * high_52:
                tech_list.append(stock.replace(".NS", ""))

                income = ticker.quarterly_financials
                if not income.empty and len(income.columns) >= 4:
                    latest_rev = income.iloc[0, 0]
                    prev_rev = income.iloc[0, 3]

                    if latest_rev > prev_rev:
                        growth_list.append(stock.replace(".NS", ""))

                        earnings = ticker.quarterly_earnings
                        if earnings is not None and len(earnings) >= 4:
                            latest_eps = earnings["Earnings"].iloc[-1]
                            prev_eps = earnings["Earnings"].iloc[-4]

                            info = ticker.info
                            roe = info.get("returnOnEquity", 0)

                            if latest_eps > prev_eps and roe and roe >= 0.20:
                                final_list.append(stock.replace(".NS", ""))

        except:
            continue

    message = "📊 Raxit Engine Scan\n\n"

    if tech_list:
        message += "Near 52W High:\n"
        for s in tech_list:
            message += f"- {s}\n"
        message += "\n"

    if growth_list:
        message += "Revenue Growing:\n"
        for s in growth_list:
            message += f"- {s}\n"
        message += "\n"

    if final_list:
        message += "🔥 Full Raxit Criteria:\n"
        for s in final_list:
            message += f"- {s}\n"
    else:
        message += "No stocks passed full Raxit criteria today."

    send_telegram(message)


if __name__ == "__main__":
    main()
