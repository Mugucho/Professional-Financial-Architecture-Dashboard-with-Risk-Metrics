import numpy as np


def find_complex_patterns(df):
    """
    Marca el DataFrame y devuelve un resumen de señales.
    """
    # 1. Asegurar columna de patrones
    if "Pattern_Detected" not in df.columns:
        df["Pattern_Detected"] = 0

    # Diccionario para evitar el KeyError en el dashboard
    signals = {"IHS": False}

    prices = df["Close"].values

    # 2. Lógica de detección (Tu código de Colab)
    for i in range(5, len(prices)):
        window = prices[i - 5 : i]
        a, b, c, d, e = window
        # Lógica geométrica de IHS
        if (
            a < b
            and c < a
            and c < e
            and c < d
            and e < d
            and abs(b - d) <= np.mean([b, d]) * 0.02
        ):
            # Marcamos el DataFrame para la GRÁFICA
            df.at[df.index[i], "Pattern_Detected"] = "IHS"
            # Activamos la señal para el DASHBOARD
            signals["IHS"] = True

    return df, signals
