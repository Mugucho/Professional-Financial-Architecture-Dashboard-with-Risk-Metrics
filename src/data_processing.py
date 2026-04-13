import pandas as pd
import numpy as np
import pandas_ta as ta


def process_data(data: pd.DataFrame, ma_window: int = 50) -> pd.DataFrame:
    if data.empty:
        return data

    df = data.copy()
    # Indicadores básicos
    df["Daily Return"] = df["Close"].pct_change()
    df["MA"] = df["Close"].rolling(window=ma_window).mean()
    df["Volatility"] = df["Daily Return"].rolling(window=20).std() * np.sqrt(252)

    # RSI (Genera columna RSI_14)
    df.ta.rsi(length=14, append=True)

    # Detección de Patrones de Velas
    cdl_patterns = df.ta.cdl_pattern(name="all")
    df = pd.concat([df, cdl_patterns], axis=1)

    # Lógica de señales para el Bot y Visualización
    df["Pattern_Detected"] = 0
    # Buscamos columnas de patrones alcistas comunes
    alcistas = [
        c
        for c in df.columns
        if any(p in c for p in ["HAMMER", "MORNINGSTAR", "ENGULFING"])
    ]
    for col in alcistas:
        # Si el valor > 0, marcamos patrón detectado
        df["Pattern_Detected"] = np.where(df[col] > 0, 1, df["Pattern_Detected"])

    return df.dropna()
