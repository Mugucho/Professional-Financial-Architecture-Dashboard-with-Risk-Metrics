import plotly.graph_objects as go
import pandas as pd


def create_candlestick_chart(data, ticker):
    """Genera el gráfico de velas con marcadores de patrones integrados."""
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

    # DIBUJAR MARCADORES: Aquí es donde verás el "IHS"
    if "Pattern_Detected" in data.columns:
        hits = data[data["Pattern_Detected"] != 0]
        if not hits.empty:
            fig.add_trace(
                go.Scatter(
                    x=hits["Date"],
                    y=hits["High"] * 1.01,
                    mode="markers+text",
                    text=hits["Pattern_Detected"],
                    textposition="top center",
                    marker=dict(
                        symbol="triangle-down",
                        size=12,
                        color="#00FFA3",
                        line=dict(width=1, color="white"),
                    ),
                    name="Patrón Detectado",
                )
            )

    fig.update_layout(
        title=f"Arquitectura Técnica: {ticker}",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=600,
    )
    return fig


def create_patterns_only_chart(data, ticker):
    """Gráfico de la pestaña 2: Psicología con estrellas doradas."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Close"],
            name="Cierre",
            line=dict(color="rgba(156, 163, 175, 0.7)", width=2),
        )
    )

    if "Pattern_Detected" in data.columns:
        hits = data[data["Pattern_Detected"] != 0]
        if not hits.empty:
            fig.add_trace(
                go.Scatter(
                    x=hits["Date"],
                    y=hits["Low"] * 0.99,
                    mode="markers+text",
                    text=hits["Pattern_Detected"],
                    textposition="bottom center",
                    marker=dict(
                        symbol="star",
                        size=15,
                        color="gold",
                        line=dict(width=1, color="white"),
                    ),
                    name="Punto de Inversión",
                )
            )
    fig.update_layout(
        title=f"Psicología de Patrones: {ticker}", template="plotly_dark", height=500
    )
    return fig


def create_rsi_chart(data):
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


def create_volume_analysis_chart(data):
    """
    Analiza la fuerza del mercado comparando el volumen actual
    con su media móvil de 20 días (Lógica de Untitled44).
    """
    fig = go.Figure()

    # 1. Barras de Volumen
    fig.add_trace(
        go.Bar(
            x=data["Date"],
            y=data["Volume"],
            name="Volumen Diario",
            marker_color="#3B82F6",  # Azul profesional
            opacity=0.7,
        )
    )

    # 2. Línea de Promedio de Volumen (Media 20)
    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Vol_Avg"],
            name="Media 20d",
            line=dict(color="orange", width=2),
        )
    )

    fig.update_layout(
        title="Análisis de Fuerza: Volumen Relativo",
        template="plotly_dark",
        xaxis_title="Fecha",
        yaxis_title="Volumen",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_daily_returns_histogram(data):
    """
    Muestra la distribución de retornos para análisis de riesgo (Lógica de Untitled42).
    """
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=data["Daily Return"], nbinsx=50, marker_color="#EF4444", name="Frecuencia"
        )
    )

    fig.update_layout(
        title="Distribución de Retornos (Riesgo)",
        template="plotly_dark",
        height=350,
        xaxis_title="Retorno Diario",
        yaxis_title="Frecuencia",
    )
    return fig
