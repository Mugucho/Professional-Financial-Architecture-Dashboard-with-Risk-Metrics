import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import os


def get_historical_macro_events(ticker, start_date, end_date):
    """
    Busca eventos significativos en un rango de fechas.
    Nota: Usamos NewsAPI (versión 'everything') filtrando por relevancia.
    """
    api_key = os.getenv("NEWS_API_KEY")
    # Convertimos fechas a string para la API
    s_date = start_date.strftime("%Y-%m-%d")
    e_date = end_date.strftime("%Y-%m-%d")

    # Buscamos términos clave: FED, Guerra, Elecciones, GDP, Inflation
    query = (
        f"{ticker} OR (stock market AND (FED OR geopolitics OR president OR inflation))"
    )
    url = f"https://newsapi.org/v2/everything?q={query}&from={s_date}&to={e_date}&sortBy=relevancy&language=en&apiKey={api_key}"

    try:
        response = requests.get(url)
        articles = response.json().get("articles", [])
        # Tomamos los 10 más relevantes para no saturar la gráfica
        events = []
        for art in articles[:10]:
            events.append(
                {
                    "Date": art["publishedAt"][:10],
                    "Title": art["title"],
                    "Description": art["description"],
                }
            )
        return events
    except:
        return []


def create_macro_chart(df, events, ticker):
    """
    Crea el gráfico maestro interactivo con subplots.
    """
    # Subplot 1: Precio (80%) | Subplot 2: Volumen (20%)
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3]
    )

    # 1. Línea de Precio
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Close"],
            name="Precio",
            line=dict(color="#00FFA3", width=2),
        ),
        row=1,
        col=1,
    )

    # 2. Marcadores de Eventos (La Magia)
    event_dates = [e["Date"] for e in events]
    # Filtramos el precio en esas fechas para ubicar el marcador
    event_prices = df[df["Date"].isin(event_dates)]

    for event in events:
        # Buscamos el precio de cierre en esa fecha para poner el punto
        price_at_date = df[df["Date"] == event["Date"]]["Close"]
        if not price_at_date.empty:
            fig.add_trace(
                go.Scatter(
                    x=[event["Date"]],
                    y=[price_at_date.values[0]],
                    mode="markers+text",
                    marker=dict(
                        symbol="hexagon",
                        size=15,
                        color="gold",
                        line=dict(width=2, color="white"),
                    ),
                    text="📢",
                    textposition="top center",
                    hovertext=f"<b>{event['Title']}</b><br>{event['Description'][:150]}...",
                    hoverinfo="text",
                    name="Evento Macro",
                ),
                row=1,
                col=1,
            )

    # 3. Volumen
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["Volume"],
            name="Volumen",
            marker_color="#3B82F6",
            opacity=0.5,
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        template="plotly_dark",
        height=700,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        title=f"Impacto Geopolítico y Económico: {ticker}",
    )
    return fig
