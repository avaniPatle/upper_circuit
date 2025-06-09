import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

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
            lc_price = data[symbol]['lower_circuit_limit']
            if ltp == uc_price or ltp == lc_price:
                tsym = symbol.replace("NSE:", "")
                uc_stocks.append({
                    "Symbol": tsym,
                    "Company Name": symbol_name_map.get(tsym, "N/A"),
                    "LTP": ltp,
                    "Upper Circuit": uc_price,
                    "Lower Circuit": lc_price,
                    "Hit": "UC" if ltp == uc_price else "LC"
                })
    except Exception as e:
        print(f"Error fetching batch {i//50 + 1}: {e}")
    time.sleep(1)

df = pd.DataFrame(uc_stocks)
df_uc = df[df["Hit"] == "UC"].drop(columns=["Hit","Lower Circuit"]).reset_index(drop=True)
df_lc = df[df["Hit"] == "LC"].drop(columns=["Hit","Upper Circuit"]).reset_index(drop=True)

st.title("NSE Circuit Breaker Stocks")

st.write(f"**Upper Circuit Stocks:** {len(df_uc)}")
st.write(f"**Lower Circuit Stocks:** {len(df_lc)}")

st.header("Upper Circuit Stocks")
st.dataframe(df_uc)

st.header("Lower Circuit Stocks")
st.dataframe(df_lc)

st.download_button(
    label="Download Upper Circuit Stocks as CSV",
    data=df_uc.to_csv(index=False),
    file_name="upper_circuit_stocks.csv",
    mime="text/csv"
)

st.download_button(
    label="Download Lower Circuit Stocks as CSV",
    data=df_lc.to_csv(index=False),
    file_name="lower_circuit_stocks.csv",
    mime="text/csv"
)
