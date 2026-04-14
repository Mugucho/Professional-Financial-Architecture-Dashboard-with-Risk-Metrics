import os
import requests
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()


def get_market_sentiment(ticker):
    """
    EL ORÁCULO DE SENTIMIENTO.
    Busca las últimas noticias financieras sobre el ticker y realiza
    un análisis de polaridad (positivo/negativo/neutral).
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "⚠️ Clave de NewsAPI no configurada en .env", 0.0

    # Buscamos noticias relevantes al ticker de las últimas semanas
    url = f"https://newsapi.org/v2/everything?q={ticker} stock market&sortBy=relevancy&language=en&pageSize=15&apiKey={api_key}"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("status") != "ok":
            return f"❌ Error API: {data.get('message', 'Desconocido')}", 0.0

        articles = data.get("articles", [])
        if not articles:
            return f"📭 No se encontraron noticias recientes para {ticker}.", 0.0

        # Procesamiento de Lenguaje Natural (NLP) con TextBlob
        polaridad_total = 0
        for article in articles:
            titulo = article.get("title", "")
            descripcion = article.get("description", "")
            # Analizamos título y descripción juntos
            texto_completo = f"{titulo}. {descripcion}"
            blob = TextBlob(texto_completo)
            polaridad_total += blob.sentiment.polarity

        polaridad_promedio = polaridad_total / len(articles)

        # Clasificación del sentimiento
        if polaridad_promedio > 0.15:
            sentimiento = "🟢 Euforia / Positivo"
        elif polaridad_promedio < -0.05:
            # Los mercados financieros tienen un sesgo positivo natural,
            # por lo que un número ligeramente negativo ya indica pánico o pesimismo.
            sentimiento = "🔴 Pánico / Negativo"
        else:
            sentimiento = "⚖️ Neutral / Consolidación"

        return sentimiento, polaridad_promedio

    except Exception as e:
        return f"🔌 Error de conexión: {str(e)}", 0.0
