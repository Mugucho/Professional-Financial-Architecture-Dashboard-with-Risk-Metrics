import yfinance as yf
import pandas as pd


def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return pd.DataFrame()
        df.index.name = "Date"
        return df
    except Exception as e:
        print(f"Error en fetcher: {e}")
        return pd.DataFrame()
