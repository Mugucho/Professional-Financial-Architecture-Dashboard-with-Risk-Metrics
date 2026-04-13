import plotly.graph_objects as go
import plotly.express as px


def create_candlestick_chart(data, ticker):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data["Date"],
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name=ticker,
            )
        ]
    )

    # Marcadores de patrones en el gráfico principal
    hits = data[data["Pattern_Detected"] != 0]
    if not hits.empty:
        fig.add_trace(
            go.Scatter(
                x=hits["Date"],
                y=hits["High"] * 1.02,
                mode="markers",
                name="Patrón Detectado",
                marker=dict(symbol="diamond", size=10, color="yellow"),
            )
        )
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        title=f"Velas: {ticker}",
    )
    return fig


def create_patterns_only_chart(data, ticker):
    """Pestaña dedicada exclusivamente a patrones de velas."""
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data["Date"],
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name=ticker,
            )
        ]
    )

    # Resaltar con etiquetas de texto
    patterns = [
        c
        for c in data.columns
        if any(p in c for p in ["HAMMER", "MORNINGSTAR", "ENGULFING"])
    ]
    for p in patterns:
        hits = data[data[p] > 0]
        if not hits.empty:
            fig.add_trace(
                go.Scatter(
                    x=hits["Date"],
                    y=hits["Low"] * 0.98,
                    mode="markers+text",
                    name=p,
                    text=[p.split("_")[-1]] * len(hits),
                    textposition="bottom center",
                    marker=dict(symbol="triangle-up", size=12, color="cyan"),
                )
            )
    fig.update_layout(
        xaxis_rangeslider_visible=True,
        template="plotly_dark",
        title="Detector de Velas",
    )
    return fig


def create_rsi_chart(data):
    rsi_col = [c for c in data.columns if "RSI" in c][0]
    fig = go.Figure(
        go.Scatter(
            x=data["Date"], y=data[rsi_col], name="RSI", line=dict(color="violet")
        )
    )
    fig.add_hline(y=70, line_dash="dot", line_color="red")
    fig.add_hline(y=30, line_dash="dot", line_color="green")
    fig.update_layout(
        template="plotly_dark", title="Momentum RSI", yaxis=dict(range=[0, 100])
    )
    return fig


def create_moving_average_chart(data, ticker, ma_window):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="Precio"))
    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["MA"],
            name=f"SMA {ma_window}",
            line=dict(dash="dash"),
        )
    )
    fig.update_layout(template="plotly_dark", title="Tendencia SMA")
    return fig


def create_daily_returns_histogram(data):
    return px.histogram(
        data, x="Daily Return", nbins=50, template="plotly_dark", title="Riesgo"
    )


def create_volume_vs_close_scatter(data):
    return px.scatter(
        data, x="Volume", y="Close", color="Daily Return", template="plotly_dark"
    )


def create_high_low_chart(data):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Date"], y=data["High"], name="High", line=dict(color="green")
        )
    )
    fig.add_trace(
        go.Scatter(x=data["Date"], y=data["Low"], name="Low", line=dict(color="red"))
    )
    fig.update_layout(template="plotly_dark")
    return fig
