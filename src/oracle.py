import requests
import pandas as pd
from textblob import TextBlob
from datetime import datetime, timedelta
import streamlit as st


def get_finnhub_news(symbol):
    """Obtiene noticias institucionales de Finnhub (Gratis y Pro)."""
    api_key = st.secrets["FINNHUB_API_KEY"]

    # Buscamos noticias de la última semana
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []


def analyze_sentiment(news_list):
    """Analiza el sentimiento de los titulares de Finnhub."""
    if not news_list:
        return 0, "Neutral"

    sentiments = []
    for item in news_list[:15]:  # Analizamos los últimos 15 titulares
        analysis = TextBlob(item["headline"])
        sentiments.append(analysis.sentiment.polarity)

    avg_sentiment = sum(sentiments) / len(sentiments)

    if avg_sentiment > 0.15:
        return avg_sentiment, "Bullish 🟢"
    elif avg_sentiment < -0.15:
        return avg_sentiment, "Bearish 🔴"
    else:
        return avg_sentiment, "Neutral 🟡"
