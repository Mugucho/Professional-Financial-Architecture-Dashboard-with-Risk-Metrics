import pandas as pd
import numpy as np
import plotly.graph_objects as go


def run_backtest(df, initial_capital=10000):
    """
    Simulador de Estrategia Histórica.
    Regla base: Compra cuando detecta un patrón y el precio está sobre la SMA.
    Mantiene la posición por 5 días para evaluar el impulso.
    """
    bt_df = df.copy()

    # 1. Generar Señales (1 = Comprar, 0 = Esperar)
    bt_df["Signal"] = 0
    if "Pattern_Detected" in bt_df.columns and "SMA" in bt_df.columns:
        # Condición: Hay patrón Y estamos en tendencia alcista (Precio > SMA)
        buy_cond = (bt_df["Pattern_Detected"] != "") & (bt_df["Close"] > bt_df["SMA"])
        bt_df.loc[buy_cond, "Signal"] = 1

    # 2. Simular Posición (Mantener por 5 periodos tras la señal)
    bt_df["Position"] = bt_df["Signal"].replace(0, np.nan).ffill(limit=5).fillna(0)

    # 3. Calcular Retornos
    # El retorno de la estrategia es el retorno diario del mercado * nuestra posición (1 o 0)
    bt_df["Strategy_Return"] = bt_df["Position"].shift(1) * bt_df["Daily Return"]

    # 4. Calcular Crecimiento del Capital (Equity Curve)
    bt_df["Cumulative_Market"] = (1 + bt_df["Daily Return"]).cumprod() * initial_capital
    bt_df["Cumulative_Strategy"] = (
        1 + bt_df["Strategy_Return"]
    ).cumprod() * initial_capital

    # 5. Métricas de Rendimiento
    total_return = (
        bt_df["Cumulative_Strategy"].iloc[-1] - initial_capital
    ) / initial_capital
    market_return = (
        bt_df["Cumulative_Market"].iloc[-1] - initial_capital
    ) / initial_capital

    # Drawdown (Peor caída desde un pico histórico)
    rolling_max = bt_df["Cumulative_Strategy"].cummax()
    drawdown = (bt_df["Cumulative_Strategy"] - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    metrics = {
        "Retorno Estrategia": total_return,
        "Retorno Mercado (Hold)": market_return,
        "Peor Caída (Max Drawdown)": max_drawdown,
    }

    return bt_df, metrics


def create_equity_curve_chart(bt_df, ticker):
    """Genera la gráfica de comparación de capital."""
    fig = go.Figure()
    # Curva del mercado (Comprar y sostener)
    fig.add_trace(
        go.Scatter(
            x=bt_df["Date"],
            y=bt_df["Cumulative_Market"],
            name="Mercado (Hold)",
            line=dict(color="gray", width=1.5),
        )
    )
    # Curva de nuestra estrategia
    fig.add_trace(
        go.Scatter(
            x=bt_df["Date"],
            y=bt_df["Cumulative_Strategy"],
            name="Estrategia AI",
            line=dict(color="#00FFA3", width=2.5),
        )
    )

    fig.update_layout(
        title=f"Prueba Histórica de Capital (Backtest): {ticker}",
        template="plotly_dark",
        height=400,
        yaxis_title="Capital ($)",
    )
    return fig
