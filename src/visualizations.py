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
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        title=f"Acción del Precio: {ticker}",
    )
    return fig


def create_moving_average_chart(data, ticker, ma_window):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="Precio Cierre"))
    fig.add_trace(
        go.Scatter(x=data["Date"], y=data["MA"], name=f"Media Móvil ({ma_window}d)")
    )
    fig.update_layout(template="plotly_dark", title=f"Análisis de Tendencia: {ticker}")
    return fig


def create_daily_returns_histogram(data):
    fig = px.histogram(
        data, x="Daily Return", nbins=50, title="Distribución de Retornos Diarios"
    )
    fig.add_vline(x=0, line_dash="dash", line_color="red")
    fig.update_layout(template="plotly_dark")
    return fig


def create_volume_vs_close_scatter(data):
    fig = px.scatter(
        data,
        x="Volume",
        y="Close",
        title="Volumen vs. Precio Cierre",
        hover_data=["Date"],
    )
    fig.update_layout(template="plotly_dark")
    return fig


def create_high_low_chart(data):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Date"], y=data["High"], name="Máximo", line=dict(color="green")
        )
    )
    fig.add_trace(
        go.Scatter(x=data["Date"], y=data["Low"], name="Mínimo", line=dict(color="red"))
    )
    fig.update_layout(template="plotly_dark", title="Rango de Precios Diarios")
    return fig


def create_rsi_chart(data):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=data["Date"], y=data["RSI"], name="RSI", line=dict(color="violet"))
    )
    fig.add_hline(y=70, line_dash="dot", line_color="red")
    fig.add_hline(y=30, line_dash="dot", line_color="green")
    fig.update_layout(
        template="plotly_dark",
        title="Indicador de Momentum (RSI)",
        yaxis=dict(range=[0, 100]),
    )
    return fig
