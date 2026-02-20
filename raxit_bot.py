import os
import requests
import pandas as pd
import yfinance as yf

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# --- Sample stock universe (start small to test)
STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "LT.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "BHARTIARTL.NS"
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
            return None

        # --- FINANCIAL DATA
        financials = ticker.financials
        income = ticker.quarterly_financials

        if income.empty or financials.empty:
            return None

        # Quarterly revenue YoY
        if len(income.columns) < 4:
            return None

        latest_rev = income.iloc[0, 0]
        prev_rev = income.iloc[0, 3]

        if latest_rev <= prev_rev:
            return None

        # Quarterly EPS YoY
        earnings = ticker.quarterly_earnings
        if earnings is None or len(earnings) < 4:
            return None

        latest_eps = earnings["Earnings"].iloc[-1]
        prev_eps = earnings["Earnings"].iloc[-4]

        if latest_eps <= prev_eps:
            return None

        # ROCE approx using ROE proxy (Yahoo limitation)
        info = ticker.info
        roe = info.get("returnOnEquity", 0)

        if roe is None or roe < 0.20:
            return None

        return symbol.replace(".NS", "")

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
    results = []

    for stock in STOCKS:
        result = check_stock(stock)
        if result:
            results.append(result)

    if results:
        msg = "📊 Raxit Engine v1 Results\n\n"
        for i, stock in enumerate(results, 1):
            msg += f"{i}. {stock}\n"
    else:
        msg = "No stocks matched Raxit criteria today."

    send_telegram(msg)


if __name__ == "__main__":
    main()
