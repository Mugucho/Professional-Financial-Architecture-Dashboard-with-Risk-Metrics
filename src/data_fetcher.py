import yfinance as yf
import pandas as pd


def fetch_stock_data(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d")
        if data.empty:
            return pd.DataFrame()
        # Aplanar MultiIndex de Yahoo Finance
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception as e:
        print(f"Error en descarga: {e}")
        return pd.DataFrame()


def fetch_watchlist_data(tickers):
    summary = []
    for symbol in tickers:
        try:
            t = yf.Ticker(symbol)
            info = t.fast_info
            price = info["last_price"]
            prev_close = info["previous_close"]
            daily_change = ((price - prev_close) / prev_close) * 100
            summary.append(
                {
                    "Ticker": symbol,
                    "Precio": round(price, 2),
                    "Var %": round(daily_change, 2),
                }
            )
        except:
            continue
    return pd.DataFrame(summary)
