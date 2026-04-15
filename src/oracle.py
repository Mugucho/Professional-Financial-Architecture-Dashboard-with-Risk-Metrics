import requests
from textblob import TextBlob
from datetime import datetime, timedelta
import streamlit as st


def get_market_sentiment(symbol):
    """
    Función principal llamada por dashboard.py.
    Obtiene noticias de Finnhub y calcula el sentimiento.
    """
    api_key = st.secrets.get("FINNHUB_API_KEY") or st.sidebar.text_input(
        "Finnhub API Key", type="password"
    )

    if not api_key:
        return 0, "Falta API Key"

    # 1. Obtener noticias
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={api_key}"

    try:
        response = requests.get(url)
        news_list = response.json() if response.status_code == 200 else []

        if not news_list:
            return 0, "Sin Noticias"

        # 2. Analizar Sentimiento
        sentiments = []
        for item in news_list[:15]:
            analysis = TextBlob(item["headline"])
            sentiments.append(analysis.sentiment.polarity)

        avg_sentiment = sum(sentiments) / len(sentiments)

        # 3. Clasificación
        if avg_sentiment > 0.15:
            return avg_sentiment, "Bullish 🟢"
        elif avg_sentiment < -0.15:
            return avg_sentiment, "Bearish 🔴"
        else:
            return avg_sentiment, "Neutral 🟡"

    except Exception as e:
        return 0, f"Error: {str(e)}"
