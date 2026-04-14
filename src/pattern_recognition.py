import pandas as pd
import pandas_ta as ta
import numpy as np


def find_complex_patterns(df):
    """
    Detecta patrones usando pandas_ta y lógica de picos/valles.
    """
    if "Pattern_Detected" not in df.columns:
        df["Pattern_Detected"] = ""

    signals = {}

    # 1. Detección de patrones de velas vía pandas_ta
    try:
        # Buscamos patrones comunes: doji, hammer, engulfing, shootingstar
        patterns_df = df.ta.cdl_pattern(
            name=["doji", "hammer", "engulfing", "shootingstar"]
        )

        if patterns_df is not None:
            for col in patterns_df.columns:
                name = col.replace("CDL_", "").upper()
                # 100 o -100 indica presencia del patrón
                hits = patterns_df[patterns_df[col] != 0]
                for idx in hits.index:
                    current = df.at[idx, "Pattern_Detected"]
                    df.at[idx, "Pattern_Detected"] = (
                        name if current == "" else f"{current}+{name}"
                    )
                    signals[name] = f"Señal {name} identificada"
    except Exception as e:
        print(f"Error en motor de patrones: {e}")

    # 2. Lógica de Inverted Head and Shoulders (IHS) - Tu lógica original
    prices = df["Close"].values
    for i in range(5, len(prices)):
        window = prices[i - 5 : i]
        if len(window) < 5:
            continue
        a, b, c, d, e = window
        # Estructura de reversión geométrica
        if (
            a < b
            and c < a
            and c < e
            and c < d
            and e < d
            and abs(b - d) <= np.mean([b, d]) * 0.02
        ):
            df.at[df.index[i], "Pattern_Detected"] = "IHS"
            signals["IHS"] = "Inverted Head and Shoulders Detectado"

    return df, signals
