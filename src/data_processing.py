import pandas as pd
import numpy as np


def process_data(df, ma_window):
    """Calcula indicadores técnicos base."""
    df["SMA"] = df["Close"].rolling(window=ma_window).mean()
    # RSI
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    # Volumen
    df["Vol_Avg"] = df["Volume"].rolling(window=20).mean()
    df["Rel_Vol"] = df["Volume"] / df["Vol_Avg"]
    # Retornos para riesgo
    df["Daily Return"] = df["Close"].pct_change()
    return df


def calculate_support_resistance(df, window=50):
    """Identifica el suelo y techo del mercado basado en extremos recientes."""
    df["Support_Level"] = df["Low"].rolling(window=window).min()
    df["Resistance_Level"] = df["High"].rolling(window=window).max()
    return df
