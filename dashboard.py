import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Importaciones de Alpaca (Sintaxis 2026)
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetPortfolioHistoryRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Importaciones desde tu estructura /src en GitHub
from src.data_fetcher import fetch_stock_data, fetch_watchlist_data
from src.data_processing import process_data
from src.pattern_recognition import find_complex_patterns
from src.visualizations import *

# 1. Configuración Inicial y Carga de Entorno
load_dotenv()
st.set_page_config(page_title="Market Architect Pro", layout="wide")

# --- SIDEBAR: Sentinel Control ---
st.sidebar.title("🏛️ Sentinel Control")
mis_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "META"]
selected = st.sidebar.selectbox("Mi Watchlist (Colab)", [""] + mis_tickers)
manual_ticker = st.sidebar.text_input("Ticker Manual", value="AAPL").upper()
ticker = selected if selected else manual_ticker

ma_window = st.sidebar.slider("Ventana SMA", 5, 200, 50)
override_rsi = st.sidebar.checkbox("Ajuste Manual RSI")
manual_rsi = st.sidebar.slider("Valor RSI", 0, 100, 50, disabled=not override_rsi)

# --- CONEXIÓN ALPACA ---
key = os.getenv("ALPACA_API_KEY")
secret = os.getenv("ALPACA_SECRET_KEY")

st.title(f"Market Architect Pro: {ticker}")

# Inicializamos el cliente de Alpaca
tc = None
if key and secret:
    try:
        tc = TradingClient(key, secret, paper=True)
        # Fix: Petición de historial de portafolio
        req_hist = GetPortfolioHistoryRequest(period="1M", timeframe="1D")
        hist = tc.get_portfolio_history(req_hist)

        c1, c2, c3 = st.columns(3)
        c1.metric("Equity Cuenta", f"${hist.equity[-1]:,.2f}")
        c2.metric("P/L Diario %", f"{hist.profit_loss_pct[-1]:.2%}")
        c3.metric("Status", "Conectado ✅")
    except Exception as e:
        st.sidebar.warning(f"Error de conexión Alpaca: {e}")

st.markdown("---")

# --- MOTOR DE PROCESAMIENTO ---
raw_data = fetch_stock_data(ticker)

if not raw_data.empty:
    # A. Procesamiento base
    data = process_data(raw_data.reset_index(), ma_window)

    # B. Detección de Patrones (Retorno doble para evitar KeyError)
    # data: DataFrame con columna 'Pattern_Detected' | signals: Diccionario {'IHS': True/False}
    data, signals = find_complex_patterns(data)

    final_rsi = manual_rsi if override_rsi else data["RSI"].iloc[-1]

    # --- NAVEGACIÓN POR PESTAÑAS (5 Pestañas) ---
    t1, t2, t3, t4, t5 = st.tabs(
        [
            "📊 Análisis Técnico",
            "🕯️ Patrones Candlestick",
            "⚠️ Riesgo y Volumen",
            "🤖 Trading Bot / Alpaca",
            "📑 Datos Crudos",
        ]
    )

    with t1:
        # Gráfica principal y RSI
        st.plotly_chart(create_candlestick_chart(data, ticker), width="stretch")
        st.plotly_chart(create_rsi_chart(data), width="stretch")

    with t2:
        st.subheader("Psicología de Patrones e Indicadores")
        # Mensaje de éxito basado en la señal detectada
        if signals.get("IHS", False):
            st.success("🚀 Patrón IHS Detectado: ¡Alerta de Alquimia Alcista!")
        else:
            st.info("No se detectan patrones complejos en el rango actual.")

        # Gráfica con estrellas doradas en puntos de inversión
        st.plotly_chart(create_patterns_only_chart(data, ticker), width="stretch")

    with t3:
        st.subheader("Fuerza de Volumen y Distribución de Riesgo")
        st.plotly_chart(create_volume_analysis_chart(data), width="stretch")
        st.plotly_chart(create_daily_returns_histogram(data), width="stretch")
        st.metric("Volumen Relativo (Z-Score)", f"{data['Rel_Vol'].iloc[-1]:.2f}x")

    with t4:
        st.subheader("⚡ Ejecución en Tiempo Real (Paper Trading)")
        if tc:
            col_q, col_s = st.columns(2)
            with col_q:
                qty = st.number_input(
                    "Cantidad de acciones", min_value=1, value=1, step=1
                )
            with col_s:
                side = st.selectbox("Operación", ["BUY", "SELL"])

            st.write(f"Orden lista para: **{ticker}** | RSI Actual: `{final_rsi:.2f}`")

            if st.button(f"🚀 Ejecutar {side} en Alpaca", width="stretch"):
                try:
                    # Construcción de la orden real
                    order_data = MarketOrderRequest(
                        symbol=ticker,
                        qty=qty,
                        side=OrderSide.BUY if side == "BUY" else OrderSide.SELL,
                        time_in_force=TimeInForce.GTC,
                    )
                    # Envío al mercado
                    order = tc.submit_order(order_data=order_data)
                    st.success(f"✅ Orden de {side} enviada con éxito.")
                    st.json(
                        {
                            "ID_Orden": order.id,
                            "Estado": order.status,
                            "Ticker": order.symbol,
                        }
                    )
                except Exception as e:
                    st.error(f"Error en la ejecución: {e}")
        else:
            st.error("No hay conexión con Alpaca. Revisa tu archivo .env")

    with t5:
        st.subheader("Explorador de Datos Finales")
        st.dataframe(data.tail(100), width="stretch")

else:
    st.error(f"No se pudieron obtener datos para el ticker: {ticker}")
