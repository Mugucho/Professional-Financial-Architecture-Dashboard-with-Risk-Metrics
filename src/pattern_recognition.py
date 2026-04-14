import pandas as pd
import pandas_ta as ta
import numpy as np


def find_complex_patterns(df):
    """
    Detecta patrones usando pandas_ta (Cloud Friendly) y lógica personalizada.
    Mantiene la compatibilidad con el Dashboard de Market Architect Pro.
    """
    if "Pattern_Detected" not in df.columns:
        df["Pattern_Detected"] = ""

    signals = {}

    # 1. Patrones de Velas con pandas_ta
    # Generamos un DataFrame temporal con los patrones seleccionados
    try:
        patterns_df = df.ta.cdl_pattern(
            name=["doji", "hammer", "engulfing", "shootingstar"]
        )

        if patterns_df is not None:
            # Mapeamos los resultados al formato de tu Dashboard
            for col in patterns_df.columns:
                # Limpiamos el nombre: 'CDL_DOJI' -> 'DOJI'
                name = col.replace("CDL_", "").upper()

                # pandas_ta devuelve 100 para alcista y -100 para bajista
                # Buscamos donde el valor no sea 0
                hits = patterns_df[patterns_df[col] != 0]
                for idx in hits.index:
                    current = df.at[idx, "Pattern_Detected"]
                    # Si ya hay un patrón, lo concatenamos con '+'
                    df.at[idx, "Pattern_Detected"] = (
                        name if current == "" else f"{current}+{name}"
                    )
                    signals[name] = f"Patrón {name} Detectado vía Pandas_TA"
    except Exception as e:
        print(f"Aviso: Error en detección de velas: {e}")

    # 2. Lógica Manual para Inverted Head and Shoulders (IHS)
    # Mantenemos tu arquitectura de picos y valles original
    prices = df["Close"].values
    for i in range(5, len(prices)):
        window = prices[i - 5 : i]
        if len(window) < 5:
            continue
        a, b, c, d, e = window
        # Lógica de estructura: hombro-cabeza-hombro invertido
        if (
            a < b
            and c < a
            and c < e
            and c < d
            and e < d
            and abs(b - d) <= np.mean([b, d]) * 0.02
        ):
            df.at[df.index[i], "Pattern_Detected"] = "IHS"
            signals["IHS"] = "Inverted Head and Shoulders (Estructura de Reversión)"

    return df, signals
