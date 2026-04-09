import yfinance as yf
import pandas as pd


def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Extrae datos históricos de Yahoo Finance de forma robusta.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty:
            return pd.DataFrame()

        return df
    except Exception as e:
        print(f"Error crítico al obtener {ticker}: {e}")
        return pd.DataFrame()
