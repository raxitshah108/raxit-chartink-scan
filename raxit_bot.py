import os
import requests
import pandas as pd
import yfinance as yf

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

STOCKS = [

# --- NIFTY 50 ---
"RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
"SBIN.NS","LT.NS","ITC.NS","KOTAKBANK.NS","AXISBANK.NS",
"HCLTECH.NS","MARUTI.NS","BAJFINANCE.NS","BHARTIARTL.NS",
"ASIANPAINT.NS","SUNPHARMA.NS","ULTRACEMCO.NS","TITAN.NS",
"NESTLEIND.NS","ADANIENT.NS","POWERGRID.NS","NTPC.NS",
"ONGC.NS","COALINDIA.NS","JSWSTEEL.NS","TATASTEEL.NS",
"HINDALCO.NS","GRASIM.NS","DIVISLAB.NS","DRREDDY.NS",
"EICHERMOT.NS","HEROMOTOCO.NS","BRITANNIA.NS","CIPLA.NS",
"APOLLOHOSP.NS","INDUSINDBK.NS","BAJAJFINSV.NS","HDFCLIFE.NS",
"SBILIFE.NS","ICICIPRULI.NS","PIDILITIND.NS","DMART.NS",
"ZOMATO.NS","ADANIPORTS.NS","ADANIGREEN.NS","ADANIPOWER.NS",
"SIEMENS.NS","ABB.NS","BHEL.NS","BEL.NS",

# --- Large & Midcaps ---
"AMBUJACEM.NS","SHREECEM.NS","ACC.NS","DLF.NS","LODHA.NS",
"INDIGO.NS","IRCTC.NS","GAIL.NS","BPCL.NS","IOC.NS",
"VEDL.NS","NMDC.NS","HAL.NS","MAZDOCK.NS","COCHINSHIP.NS",
"LTIM.NS","PERSISTENT.NS","MPHASIS.NS","COFORGE.NS",
"TATAELXSI.NS","KPITTECH.NS","POLYCAB.NS","HAVELLS.NS",
"DIXON.NS","PAGEIND.NS","MOTHERSON.NS","BOSCHLTD.NS",
"ASHOKLEY.NS","TVSMOTOR.NS","BAJAJ-AUTO.NS","ESCORTS.NS",
"CANBK.NS","PNB.NS","BANKBARODA.NS","IDFCFIRSTB.NS",
"FEDERALBNK.NS","RBLBANK.NS","AUROPHARMA.NS","TORNTPHARM.NS",
"LUPIN.NS","ALKEM.NS","BIOCON.NS","ZYDUSLIFE.NS",
"SRF.NS","DEEPAKNTR.NS","NAVINFLUOR.NS","AARTIIND.NS",
"ATUL.NS","CHAMBLFERT.NS","UPL.NS","COROMANDEL.NS",
"TATACHEM.NS","PIIND.NS","GODREJCP.NS","DABUR.NS",
"COLPAL.NS","MARICO.NS","BERGEPAINT.NS","KANSAINER.NS",
"ICICIGI.NS","HDFCAMC.NS","MUTHOOTFIN.NS","MANAPPURAM.NS",
"CHOLAFIN.NS","SHRIRAMFIN.NS","BAJAJHLDNG.NS","L&TFH.NS",

# --- Capital Goods / Infra / Defence ---
"KALPATPOWR.NS","IRB.NS","NBCC.NS","RVNL.NS","IRCON.NS",
"GRINFRA.NS","PNCINFRA.NS","KEC.NS","CGPOWER.NS",
"THERMAX.NS","SKFINDIA.NS","CUMMINSIND.NS","HONAUT.NS",
"SCHAEFFLER.NS","ISGEC.NS","JINDALSTEL.NS","RATNAMANI.NS",
"APLAPOLLO.NS","SAIL.NS","JSL.NS","JSWENERGY.NS",

# --- New Age / High Beta ---
"NYKAA.NS","PAYTM.NS","POLICYBZR.NS","DELHIVERY.NS",
"NAUKRI.NS","IRFC.NS","IREDA.NS","HUDCO.NS","GMRINFRA.NS",
"ADANITRANS.NS","ADANITOTAL.NS","TATAPOWER.NS","NHPC.NS",
"SJVN.NS","PFC.NS","RECLTD.NS","LICI.NS",

# --- Consumption / Retail ---
"TRENT.NS","VBL.NS","RADICO.NS","UBL.NS","UNITDSPR.NS",
"TATACONSUM.NS","BRIGADE.NS","OBEROIRLTY.NS","PRESTIGE.NS",
"PHOENIXLTD.NS","DLINKINDIA.NS","CROMPTON.NS","WHIRLPOOL.NS",

# --- Logistics / Ports / Shipping ---
"CONCOR.NS","SCI.NS","TCI.NS","BLUEDART.NS",
"ALLCARGO.NS","VRLLOG.NS","GESHIP.NS","JINDALSAW.NS",

# --- Others (Liquid Midcaps) ---
"SUPREMEIND.NS","ASTRAL.NS","CERA.NS","FINCABLES.NS",
"KEI.NS","VOLTAS.NS","AIAENG.NS","TIMKEN.NS",
"GLAND.NS","SONACOMS.NS","BANDHANBNK.NS","JUBLFOOD.NS",
"MRF.NS","APOLLOTYRE.NS","JKCEMENT.NS","RAMCOCEM.NS",
"IDBI.NS","BALKRISIND.NS","IEX.NS","CAMS.NS"
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
