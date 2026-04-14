import numpy as np
import talib

# Mapeo de patrones de tu archivo app.py
TALIB_PATTERNS = {
    "CDLDOJI": (talib.CDLDOJI, "Doji: Indecisión"),
    "CDLHAMMER": (talib.CDLHAMMER, "Hammer: Reversión Alcista"),
    "CDLENGULFING": (talib.CDLENGULFING, "Engulfing: Fuerte Reversión"),
    "CDLSHOOTINGSTAR": (talib.CDLSHOOTINGSTAR, "Shooting Star: Reversión Bajista"),
    "CDL3BLACKCROWS": (talib.CDL3BLACKCROWS, "3 Black Crows: Bajista Fuerte"),
    "CDL3WHITESOLDIERS": (talib.CDL3WHITESOLDIERS, "3 White Soldiers: Alcista Fuerte"),
}


def find_complex_patterns(df):
    """Detecta patrones geométricos y de velas, marcando el DataFrame."""
    # SOLUCIÓN: Inicializar con string vacío ("") en lugar de 0 para evitar el error de PyArrow
    if "Pattern_Detected" not in df.columns:
        df["Pattern_Detected"] = ""

    signals = {"IHS": False}

    # 1. Lógica de Inverted Head and Shoulders (IHS)
    prices = df["Close"].values
    for i in range(5, len(prices)):
        window = prices[i - 5 : i]
        if len(window) < 5:
            continue
        a, b, c, d, e = window
        if (
            a < b
            and c < a
            and c < e
            and c < d
            and e < d
            and abs(b - d) <= np.mean([b, d]) * 0.02
        ):
            df.at[df.index[i], "Pattern_Detected"] = "IHS"
            signals["IHS"] = True

    # 2. Lógica TA-Lib (Integración app.py)
    op, hi, lo, cl = (
        df["Open"].astype(float),
        df["High"].astype(float),
        df["Low"].astype(float),
        df["Close"].astype(float),
    )
    for code, (func, desc) in TALIB_PATTERNS.items():
        res = func(op, hi, lo, cl)
        for idx in df.index[res != 0]:
            name = code.replace("CDL", "")
            current = df.at[idx, "Pattern_Detected"]
            # SOLUCIÓN: Comparamos contra el string vacío en lugar del 0
            df.at[idx, "Pattern_Detected"] = (
                name if current == "" else f"{current}+{name}"
            )
            signals[name] = desc

    return df, signals
