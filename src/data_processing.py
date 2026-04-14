import pandas as pd
import numpy as np
import pandas_ta as ta


def process_data(df, ma_window):
    df = df.copy()

    # 1. Indicadores Base
    df["MA"] = df["Close"].rolling(window=ma_window).mean()
    df["RSI"] = ta.rsi(df["Close"], length=14)
    df["Daily Return"] = df["Close"].pct_change()

    # 2. Análisis de Fuerza de Volumen (Untitled44.ipynb)
    df["Vol_Avg"] = df["Volume"].rolling(window=20).mean()
    df["Rel_Vol"] = df["Volume"] / df["Vol_Avg"]

    # 3. Métricas de Riesgo (Untitled42.ipynb)
    df["Volatility"] = df["Daily Return"].rolling(window=21).std() * np.sqrt(252)

    # 4. Seguro contra KeyError: Creamos la columna para las visualizaciones
    df["Pattern_Detected"] = 0

    return df.dropna()
