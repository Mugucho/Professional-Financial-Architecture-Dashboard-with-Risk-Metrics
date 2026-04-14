import plotly.graph_objects as go
import pandas as pd


def create_watchlist_summary_table(tickers_data):
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


def create_candlestick_chart(data, ticker):
    fig = go.Figure()
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
    # Niveles Soportes y Resistencias
    res = data["High"].iloc[-50:].max()
    sup = data["Low"].iloc[-50:].min()
    fig.add_hline(y=res, line_dash="dot", line_color="#FF4B4B", annotation_text="RES")
    fig.add_hline(y=sup, line_dash="dot", line_color="#00FFA3", annotation_text="SUP")

    if "Pattern_Detected" in data.columns:
        hits = data[data["Pattern_Detected"] != 0]
        fig.add_trace(
            go.Scatter(
                x=hits["Date"],
                y=hits["High"] * 1.01,
                mode="markers",
                marker=dict(symbol="triangle-down", size=12, color="#00FFA3"),
            )
        )
    fig.update_layout(
        template="plotly_dark", xaxis_rangeslider_visible=False, height=600
    )
    return fig


def create_rsi_chart(data):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Date"], y=data["RSI"], name="RSI", line=dict(color="#C084FC")
        )
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")
    fig.update_layout(template="plotly_dark", height=300, yaxis=dict(range=[0, 100]))
    return fig


def create_patterns_only_chart(data, ticker):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Date"], y=data["Close"], name="Precio", line=dict(color="gray")
        )
    )
    if "Pattern_Detected" in data.columns:
        hits = data[data["Pattern_Detected"] != 0]
        fig.add_trace(
            go.Scatter(
                x=hits["Date"],
                y=hits["Low"] * 0.99,
                mode="markers+text",
                text=hits["Pattern_Detected"],
                marker=dict(symbol="star", size=15, color="gold"),
            )
        )
    fig.update_layout(template="plotly_dark", height=500)
    return fig


def create_volume_analysis_chart(data):
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
    fig.update_layout(template="plotly_dark", height=300)
    return fig


def create_daily_returns_histogram(data):
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(x=data["Daily Return"], nbinsx=50, marker_color="#EF4444")
    )
    fig.update_layout(template="plotly_dark", height=300)
    return fig
