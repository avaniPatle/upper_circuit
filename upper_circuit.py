import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("SCREENER_EMAIL")


KITE_API_KEY=os.getenv("KITE_API_KEY")
KITE_ACCESS_TOKEN=os.getenv("KITE_ACCESS_TOKEN")

kite = KiteConnect(api_key=KITE_API_KEY, access_token=KITE_ACCESS_TOKEN)
instruments = kite.instruments(exchange="NSE")

symbol_name_map = {
    inst['tradingsymbol']: inst['name']
    for inst in instruments
    if inst['segment'] == 'NSE'
}
symbols = [inst['tradingsymbol'] for inst in instruments if inst['segment'] == 'NSE']
nse_symbols = [f"NSE:{sym}" for sym in symbols]
uc_stocks = []

for i in range(0, len(nse_symbols), 50):
    batch = nse_symbols[i:i+50]
    try:
        data = kite.quote(batch)
        for symbol in batch:
            ltp = data[symbol]['last_price']
            uc_price = data[symbol]['upper_circuit_limit']
            if ltp == uc_price:
                tsym = symbol.replace("NSE:", "")
                uc_stocks.append({
                    "Symbol": tsym,
                    "Company Name": symbol_name_map.get(tsym, "N/A"),
                    "LTP": ltp,
                    "Upper Circuit": uc_price
                })
    except Exception as e:
        print(f"Error fetching batch {i//50 + 1}: {e}")

    time.sleep(1)

df = pd.DataFrame(uc_stocks)

st.title("Daily Upper Circuit Stocks")
st.dataframe(df)

st.download_button("Download as CSV", df.to_csv(index=False), "uc_stocks.csv")
