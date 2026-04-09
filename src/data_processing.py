import pandas as pd
import numpy as np


def process_data(data: pd.DataFrame, ma_window: int = 50) -> pd.DataFrame:
    """
    Calcula métricas financieras avanzadas y limpia nulos.
    """
    if data.empty:
        return data

    df = data.copy()

    # 1. Retornos Diarios
    df["Daily Return"] = df["Close"].pct_change()

    # 2. Media Móvil (MA)
    df["MA"] = df["Close"].rolling(window=ma_window).mean()

    # 3. Volatilidad Anualizada (Gestión de Riesgo)
    df["Volatility"] = df["Daily Return"].rolling(window=20).std() * np.sqrt(252)

    # 4. RSI (Relative Strength Index) - Momentum
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Limpieza de nulos iniciales para evitar errores en gráficas
    df = df.dropna()

    return df
