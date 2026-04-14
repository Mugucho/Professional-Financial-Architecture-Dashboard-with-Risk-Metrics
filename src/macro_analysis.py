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
        data = response.json()

        # Blindaje extra: si la API nos bloquea por buscar fechas muy antiguas en el plan gratis
        if data.get("status") != "ok":
            return []

        articles = data.get("articles", [])
        # Tomamos los 10 más relevantes para no saturar la gráfica
        events = []
        for art in articles[:10]:
            # BLINDAJE: Si 'description' es None, ponemos un string vacío para que no colapse
            raw_desc = art.get("description")
            safe_desc = (
                raw_desc
                if raw_desc is not None
                else "Sin descripción provista por la fuente."
            )

            events.append(
                {
                    "Date": art.get("publishedAt", "")[:10],
                    "Title": art.get("title", "Titular desconocido"),
                    "Description": safe_desc,
                }
            )
        return events
    except Exception as e:
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
    for event in events:
        # Buscamos el precio de cierre en esa fecha para poner el punto
        price_at_date = df[df["Date"] == event["Date"]]["Close"]
        if not price_at_date.empty:

            # Cortamos a 150 caracteres de forma segura ahora que sabemos que sí es un string
            short_desc = event["Description"][:150]

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
                    hovertext=f"<b>{event['Title']}</b><br>{short_desc}...",
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
