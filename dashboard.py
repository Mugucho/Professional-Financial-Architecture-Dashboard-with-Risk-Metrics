import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetPortfolioHistoryRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Importaciones desde tu estructura /src
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data, calculate_support_resistance
from src.pattern_recognition import find_complex_patterns
from src.visualizations import *
from src.risk_management import drawdown_gate, exposure_gate, reconciliation_gate

# 1. Configuración Inicial
load_dotenv()
st.set_page_config(page_title="Market Architect Pro", layout="wide")

# --- SIDEBAR: Sentinel Control ---
st.sidebar.title("🏛️ Sentinel Control")
mis_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "META"]
selected = st.sidebar.selectbox("Mi Watchlist", [""] + mis_tickers)
manual_ticker = st.sidebar.text_input("Ticker Manual", value="AAPL").upper()
ticker = selected if selected else manual_ticker

ma_window = st.sidebar.slider("Ventana SMA", 5, 200, 50)
override_rsi = st.sidebar.checkbox("Ajuste Manual RSI")
manual_rsi = st.sidebar.slider("Valor RSI", 0, 100, 50, disabled=not override_rsi)

# --- CONEXIÓN ALPACA ---
key = os.getenv("ALPACA_API_KEY")
secret = os.getenv("ALPACA_SECRET_KEY")
tc = None

if key and secret:
    try:
        tc = TradingClient(key, secret, paper=True)
        req_hist = GetPortfolioHistoryRequest(period="1M", timeframe="1D")
        hist = tc.get_portfolio_history(req_hist)

        c1, c2, c3 = st.columns(3)
        c1.metric("Equity Cuenta", f"${hist.equity[-1]:,.2f}")
        c2.metric("P/L Diario %", f"{hist.profit_loss_pct[-1]:.2%}")
        c3.metric("Status", "Conectado ✅")
    except Exception as e:
        st.sidebar.warning(f"Error Alpaca: {e}")

st.markdown("---")

# =================================================================
# 📋 RESUMEN DE WATCHLIST (RESTAURADO EXACTAMENTE COMO ESTABA)
# =================================================================
st.markdown("### 📋 Resumen de Acciones Analizadas")

processed_watchlist = {}
for t in mis_tickers:
    raw_df = fetch_stock_data(t)
    if raw_df is not None and not raw_df.empty:
        df_proc = process_data(raw_df.reset_index(), ma_window)
        processed_watchlist[t] = df_proc

if processed_watchlist:
    # 1. Métricas visuales en la parte superior (Restaurado)
    cols = st.columns(len(mis_tickers))
    for i, t_name in enumerate(mis_tickers):
        if t_name in processed_watchlist:
            d = processed_watchlist[t_name]
            if len(d) > 1:
                price = d["Close"].iloc[-1]
                prev_price = d["Close"].iloc[-2]
                change = ((price - prev_price) / prev_price) * 100
                cols[i].metric(t_name, f"${price:.2f}", f"{change:+.2f}%")

    # 2. Tabla resumen detallada
    summary_df = create_watchlist_summary_table(processed_watchlist)
    st.dataframe(summary_df, width="stretch", hide_index=True)

st.markdown("---")

# =================================================================
# --- ANÁLISIS DETALLADO DEL TICKER ---
# =================================================================
st.title(f"Análisis Técnico: {ticker}")
raw_data = fetch_stock_data(ticker)

if raw_data is not None and not raw_data.empty:
    data = process_data(raw_data.reset_index(), ma_window)

    # Soportes y Resistencias
    data = calculate_support_resistance(data)
    precio_actual = data["Close"].iloc[-1]
    soporte_actual = data["Low"].iloc[-50:].min()
    distancia_sop = ((precio_actual - soporte_actual) / soporte_actual) * 100

    st.sidebar.markdown("---")
    st.sidebar.metric("Proximidad Soporte", f"{distancia_sop:.2f}%")
    if distancia_sop < 1.5:
        st.sidebar.success("🎯 Zona de Compra: Precio en Soporte")

    # Detección de patrones
    data, signals = find_complex_patterns(data)
    final_rsi = manual_rsi if override_rsi else data["RSI"].iloc[-1]

    # --- PESTAÑAS ---
    t1, t2, t3, t4, t5 = st.tabs(
        [
            "📊 Análisis Técnico",
            "🕯️ Patrones Candlestick",
            "⚠️ Riesgo y Volumen",
            "🤖 Trading Bot / Alpaca",
            "📑 Datos",
        ]
    )

    with t1:
        st.plotly_chart(create_candlestick_chart(data, ticker), width="stretch")
        st.plotly_chart(create_rsi_chart(data), width="stretch")

    with t2:
        st.subheader("Control de Visualización de Patrones")

        # INTERRUPTOR SOLICITADO
        ver_patrones = st.toggle(
            "🔍 Mostrar símbolos de patrones en gráficos", value=True
        )

        # Mensajes de los patrones detectados
        for k, v in signals.items():
            if v:
                if k == "IHS":
                    st.success("🚀 Patrón IHS Detectado: ¡Oportunidad Alcista!")
                else:
                    st.info(f"📍 {k}: {v}")

        # Gráfico con control de visibilidad
        st.plotly_chart(
            create_patterns_only_chart(data, ticker, show_patterns=ver_patrones),
            width="stretch",
        )

    with t3:
        st.plotly_chart(create_volume_analysis_chart(data), width="stretch")
        st.plotly_chart(create_daily_returns_histogram(data), width="stretch")

    with t4:
        st.subheader("🛡️ Risk Management Pipeline")
        if tc:
            account = tc.get_account()
            is_safe, daily_pl = drawdown_gate(account, max_drawdown_pct=-0.02)

            if not is_safe:
                st.error(
                    f"🛑 DRAWDOWN GATE ACTIVADO: Tu pérdida diaria es del {daily_pl:.2%}. Bloqueado por seguridad."
                )
            else:
                st.success(f"✅ Drawdown Gate OK (P/L Diario: {daily_pl:.2%})")
                max_allowed_qty = exposure_gate(
                    account, precio_actual, max_portfolio_pct=0.10
                )
                current_position = reconciliation_gate(tc, ticker)

                st.info(
                    f"🛡️ Exposure Gate: Por riesgo, máximo puedes operar **{max_allowed_qty}** acciones."
                )
                if current_position > 0:
                    st.warning(
                        f"🔄 Reconciliation Gate: Ya posees **{current_position}** acciones de {ticker}."
                    )

                col_q, col_s = st.columns(2)
                with col_q:
                    qty = st.number_input(
                        "Cantidad",
                        min_value=1,
                        max_value=max(1, max_allowed_qty),
                        value=1,
                    )
                with col_s:
                    side = st.selectbox("Lado", ["BUY", "SELL"])

                if st.button(f"🚀 Ejecutar {side} en Alpaca", width="stretch"):
                    try:
                        order = tc.submit_order(
                            MarketOrderRequest(
                                symbol=ticker,
                                qty=qty,
                                side=OrderSide.BUY if side == "BUY" else OrderSide.SELL,
                                time_in_force=TimeInForce.GTC,
                            )
                        )
                        st.success(f"Orden {order.id} enviada.")
                        st.json({"ID": order.id, "Estado": order.status})
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.error("Conexión Alpaca no disponible.")

    with t5:
        st.dataframe(data.tail(100), width="stretch")
