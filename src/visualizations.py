import plotly.graph_objects as go
import pandas as pd

# Mapa de Símbolos para identificar patrones visualmente
SYMBOL_MAP = {
    "IHS": "star",
    "DOJI": "circle",
    "HAMMER": "triangle-up",
    "ENGULFING": "diamond",
    "SHOOTINGSTAR": "triangle-down",
}


def create_watchlist_summary_table(tickers_data):
    """Genera la tabla de resumen para la pantalla principal."""
    summary_list = []
    for ticker, df in tickers_data.items():
        if not df.empty and len(df) > 1:
            last = df.iloc[-1]
            prev = df.iloc[-2]
            change = ((last["Close"] - prev["Close"]) / prev["Close"]) * 100

            summary_list.append(
                {
                    "Ticker": ticker,
                    "Precio": f"${last['Close']:.2f}",
                    "Cambio %": f"{change:+.2f}%",
                    "RSI": round(last["RSI"], 2),
                    "Volumen Rel.": f"{last['Rel_Vol']:.2f}x",
                    "Estado": (
                        "🔥" if last["RSI"] > 70 else "❄️" if last["RSI"] < 30 else "⚖️"
                    ),
                }
            )
    return pd.DataFrame(summary_list)


def create_candlestick_chart(data, ticker, show_patterns=True):
    """Gráfico principal de la Pestaña 1: Velas y Niveles."""
    fig = go.Figure()

    # Velas Japonesas
    fig.add_trace(
        go.Candlestick(
            x=data["Date"],
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Precio",
        )
    )

    # Proyección de Soportes y Resistencias
    resistencia = data["High"].iloc[-50:].max()
    soporte = data["Low"].iloc[-50:].min()

    fig.add_hline(
        y=resistencia,
        line_dash="dot",
        line_color="#FF4B4B",
        annotation_text="RES",
        annotation_position="top right",
    )
    fig.add_hline(
        y=soporte,
        line_dash="dot",
        line_color="#00FFA3",
        annotation_text="SUP",
        annotation_position="bottom right",
    )

    # SOLUCIÓN: Se actualiza el filtro a string vacío
    if show_patterns and "Pattern_Detected" in data.columns:
        hits = data[data["Pattern_Detected"] != ""].copy()
        if not hits.empty:
            for name in hits["Pattern_Detected"].unique():
                p_hits = hits[hits["Pattern_Detected"] == name]
                base_pattern = str(name).split("+")[0].strip()
                fig.add_trace(
                    go.Scatter(
                        x=p_hits["Date"],
                        y=p_hits["High"] * 1.015,
                        mode="markers",
                        marker=dict(
                            symbol=SYMBOL_MAP.get(base_pattern, "hexagram"),
                            size=12,
                            color="white",
                        ),
                        name=f"Patrón: {name}",
                    )
                )

    fig.update_layout(
        title=f"Arquitectura de Mercado: {ticker}",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=600,
    )
    return fig


def create_rsi_chart(data):
    """Gráfico de RSI de la Pestaña 1."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["RSI"],
            name="RSI",
            line=dict(color="#C084FC", width=2),
        )
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")
    fig.update_layout(
        title="RSI (Fuerza Relativa)",
        template="plotly_dark",
        yaxis=dict(range=[0, 100]),
        height=300,
    )
    return fig


def create_patterns_only_chart(data, ticker, show_patterns=True):
    """Gráfico de la Pestaña 2: Controlado por el interruptor visual (Toggle)."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Close"],
            name="Cierre",
            line=dict(color="gray", width=1.5),
        )
    )

    # SOLUCIÓN: Se actualiza el filtro a string vacío
    if show_patterns and "Pattern_Detected" in data.columns:
        hits = data[data["Pattern_Detected"] != ""].copy()
        if not hits.empty:
            for patron_nombre in hits["Pattern_Detected"].unique():
                p_hits = hits[hits["Pattern_Detected"] == patron_nombre]

                base_name = str(patron_nombre).split("+")[0].strip()
                symbol = SYMBOL_MAP.get(base_name, "hexagram")

                fig.add_trace(
                    go.Scatter(
                        x=p_hits["Date"],
                        y=p_hits["Low"] * 0.99,
                        mode="markers+text",
                        text=patron_nombre,
                        textposition="bottom center",
                        marker=dict(
                            symbol=symbol, size=14, line=dict(width=1, color="white")
                        ),
                        name=f"{patron_nombre}",
                    )
                )

    fig.update_layout(
        title="Psicología de Patrones", template="plotly_dark", height=500
    )
    return fig


def create_volume_analysis_chart(data):
    """Gráfico de Volumen de la Pestaña 3."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=data["Date"], y=data["Volume"], name="Volumen", marker_color="#3B82F6")
    )
    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Vol_Avg"],
            name="Media 20d",
            line=dict(color="orange"),
        )
    )
    fig.update_layout(
        title="Fuerza de Volumen Relativo", template="plotly_dark", height=300
    )
    return fig


def create_daily_returns_histogram(data):
    """Gráfico de Riesgo de la Pestaña 3."""
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(x=data["Daily Return"], nbinsx=50, marker_color="#EF4444")
    )
    fig.update_layout(
        title="Distribución de Retornos (Riesgo)", template="plotly_dark", height=300
    )
    return fig
