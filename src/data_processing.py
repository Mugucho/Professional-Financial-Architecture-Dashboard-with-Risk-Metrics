import pandas as pd
import pandas_ta as ta


def process_data(df, ma_window):
    """
    Procesa indicadores técnicos usando pandas_ta.
    Optimizado para despliegue en iPad y Nube.
    """
    # 1. RSI (Relative Strength Index) - Estándar 14 periodos
    df["RSI"] = ta.rsi(df["Close"], length=14)

    # 2. SMA (Simple Moving Average) - Ventana controlada por el Sidebar
    df["SMA"] = ta.sma(df["Close"], length=ma_window)

    # 3. Retornos Diarios (Para Histogramas de Riesgo)
    df["Daily Return"] = df["Close"].pct_change()

    # 4. Análisis de Volumen Relativo
    # Calculamos la media del volumen de los últimos 20 días
    df["Vol_Avg"] = ta.sma(df["Volume"], length=20)
    df["Rel_Vol"] = df["Volume"] / df["Vol_Avg"]

    # Limpieza de valores nulos iniciales para evitar errores en gráficas
    df = df.fillna(0)

    return df


def calculate_support_resistance(df, window=50):
    """
    Cálculo dinámico de niveles institucionales.
    """
    df["Support_Level"] = df["Low"].rolling(window=window).min()
    df["Resistance_Level"] = df["High"].rolling(window=window).max()
    return df
