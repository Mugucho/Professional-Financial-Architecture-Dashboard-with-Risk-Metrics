import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

# Importaciones de Alpaca (Trading Institucional)
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetPortfolioHistoryRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Importaciones de la arquitectura modular /src
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data, calculate_support_resistance
from src.pattern_recognition import find_complex_patterns
from src.visualizations import *
from src.risk_management import drawdown_gate, exposure_gate, reconciliation_gate
from src.oracle import get_market_sentiment
from src.backtest import run_backtest, create_equity_curve_chart
from src.macro_analysis import get_historical_macro_events, create_macro_chart
from src.styles import apply_futuristic_design

# 1. Configuración del entorno y UI
load_dotenv()
st.set_page_config(page_title="Market Architect Pro", layout="wide")
apply_futuristic_design()

# --- SIDEBAR: Sentinel Control ---
st.sidebar.title("🏛️ Sentinel Control")
mis_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "META"]
selected = st.sidebar.selectbox("Mi Watchlist", [""] + mis_tickers)
manual_ticker = st.sidebar.text_input("Ticker Manual", value="AAPL").upper()
ticker = selected if selected else manual_ticker

ma_window = st.sidebar.slider("Ventana SMA", 5, 200, 50)
override_rsi = st.sidebar.checkbox("Ajuste Manual RSI")
manual_rsi = st.sidebar.slider("Valor RSI", 0, 100, 50, disabled=not override_rsi)

# --- CONEXIÓN ALPACA (Estado de Cuenta) ---
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

st.sidebar.markdown("---")
st.sidebar.caption("🏛️ **Market Architect Pro v1.0**")
st.sidebar.caption("Handcrafted by **Miguel Calle Romero**")
st.sidebar.caption("Trenton, NJ | 2026")

st.markdown("---")

# =================================================================
# 📋 RESUMEN DE WATCHLIST (Vista Panorámica)
# =================================================================
st.markdown("### 📋 Resumen de Acciones Analizadas")

processed_watchlist = {}
for t in mis_tickers:
    raw_df = fetch_stock_data(t)
    if raw_df is not None and not raw_df.empty:
        df_proc = process_data(raw_df.reset_index(), ma_window)
        processed_watchlist[t] = df_proc

if processed_watchlist:
    # Fila de métricas visuales para los 6 tickers principales
    cols = st.columns(len(mis_tickers))
    for i, t_name in enumerate(mis_tickers):
        if t_name in processed_watchlist:
            d = processed_watchlist[t_name]
            if len(d) > 1:
                price = d["Close"].iloc[-1]
                prev_price = d["Close"].iloc[-2]
                change = ((price - prev_price) / prev_price) * 100
                cols[i].metric(t_name, f"${price:.2f}", f"{change:+.2f}%")

    # Tabla resumen detallada (visualizations.py)
    summary_df = create_watchlist_summary_table(processed_watchlist)
    st.dataframe(summary_df, width="stretch", hide_index=True)

st.markdown("---")

# =================================================================
# --- ANÁLISIS DETALLADO DEL TICKER SELECCIONADO ---
# =================================================================
st.title(f"Market Architect Pro: {ticker}")
raw_data = fetch_stock_data(ticker)

if raw_data is not None and not raw_data.empty:
    data = process_data(raw_data.reset_index(), ma_window)
    data = calculate_support_resistance(data)

    # --- MÉTRICAS SIDEBAR ---
    precio_actual = data["Close"].iloc[-1]
    soporte_actual = data["Support_Level"].iloc[-1]
    distancia_sop = ((precio_actual - soporte_actual) / soporte_actual) * 100

    st.sidebar.markdown("---")
    st.sidebar.metric("Proximidad Soporte", f"{distancia_sop:.2f}%")
    if distancia_sop < 1.5:
        st.sidebar.success("🎯 Zona de Compra: Precio en Soporte")

    # --- ORÁCULO DE SENTIMIENTO (Sidebar) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔮 Oráculo de Noticias")
    if st.sidebar.button("Consultar Sentimiento Actual", use_container_width=True):
        with st.sidebar.spinner("Analizando titulares..."):
            sentimiento, score = get_market_sentiment(ticker)
            st.sidebar.info(f"**{sentimiento}**")
            st.sidebar.caption(f"Score de Polaridad: {score:.3f}")

    # Reconocimiento de patrones
    data, signals = find_complex_patterns(data)

    # --- NAVEGACIÓN POR PESTAÑAS (7 Mundos) ---
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(
        [
            "📊 Análisis Técnico",
            "🕯️ Patrones",
            "⚠️ Riesgo/Volumen",
            "🤖 Trading Bot",
            "📑 Datos",
            "📈 Backtesting",
            "🌍 Macro Impact",
        ]
    )

    with t1:
        st.plotly_chart(create_candlestick_chart(data, ticker), width="stretch")
        st.plotly_chart(create_rsi_chart(data), width="stretch")

    with t2:
        st.subheader("Psicología de Velas Japonesas")
        ver_patrones = st.toggle(
            "🔍 Visualizar símbolos de patrones en el gráfico", value=True
        )

        for k, v in signals.items():
            if v:
                if k == "IHS":
                    st.success("🚀 Patrón IHS Confirmado: Estructura Alcista")
                else:
                    st.info(f"📍 {k}: {v}")

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
            # Compuerta 1: Drawdown
            is_safe, daily_pl = drawdown_gate(account, max_drawdown_pct=-0.02)

            if not is_safe:
                st.error(
                    f"🛑 BLOQUEO DE SEGURIDAD: Pérdida diaria {daily_pl:.2%}. Operativa suspendida."
                )
            else:
                st.success(f"✅ Drawdown Gate OK (P/L Diario: {daily_pl:.2%})")
                # Compuertas 2 y 3: Exposición y Reconciliación
                max_allowed_qty = exposure_gate(
                    account, precio_actual, max_portfolio_pct=0.10
                )
                current_position = reconciliation_gate(tc, ticker)

                st.info(
                    f"🛡️ Exposure Gate: Límite sugerido de **{max_allowed_qty}** acciones."
                )
                if current_position > 0:
                    st.warning(
                        f"🔄 Reconciliation Gate: Ya posees **{current_position}** acciones."
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
                        st.success(f"Orden {order.id} enviada correctamente.")
                        st.json({"ID": order.id, "Estado": order.status})
                    except Exception as e:
                        st.error(f"Error en ejecución: {e}")
        else:
            st.error("Conexión con Alpaca no detectada.")

    with t5:
        st.dataframe(data.tail(100), width="stretch")

    with t6:
        st.subheader("📈 Simulación de Rendimiento Histórico")
        bt_data, bt_metrics = run_backtest(data, initial_capital=10000)

        m1, m2, m3 = st.columns(3)
        m1.metric("Retorno Estrategia", f"{bt_metrics['Retorno Estrategia']:.2%}")
        m2.metric("Mercado (Hold)", f"{bt_metrics['Retorno Mercado (Hold)']:.2%}")
        m3.metric("Máximo Drawdown", f"{bt_metrics['Peor Caída (Max Drawdown)']:.2%}")

        st.plotly_chart(create_equity_curve_chart(bt_data, ticker), width="stretch")

    with t7:
        st.subheader("🌍 Análisis de Impacto Geopolítico y Macro")
        st.caption(
            "Investiga cómo los eventos globales y decisiones económicas afectaron el precio en periodos específicos."
        )

        c_f1, c_f2 = st.columns(2)
        with c_f1:
            start_f = st.date_input("Fecha Inicio", value=data["Date"].iloc[0])
        with c_f2:
            end_f = st.date_input("Fecha Fin", value=data["Date"].iloc[-1])

        if st.button("Sincronizar Datos Macro", use_container_width=True):
            with st.spinner("Correlacionando eventos económicos..."):
                # Filtrado temporal para el zoom interactivo
                mask = (data["Date"] >= pd.to_datetime(start_f)) & (
                    data["Date"] <= pd.to_datetime(end_f)
                )
                filtered_data = data.loc[mask]

                # Obtención de eventos (macro_analysis.py)
                macro_events = get_historical_macro_events(ticker, start_f, end_f)

                if macro_events:
                    st.plotly_chart(
                        create_macro_chart(filtered_data, macro_events, ticker),
                        width="stretch",
                    )
                    # Listado descriptivo de los hitos
                    for e in macro_events:
                        with st.expander(f"📅 {e['Date']} - {e['Title']}"):
                            st.write(e["Description"])
                else:
                    st.warning(
                        "No se hallaron hitos específicos en el rango seleccionado con la API actual."
                    )

else:
    st.error(f"Error de conexión: No se pudieron recuperar datos para {ticker}.")
