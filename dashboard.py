import streamlit as st
import pandas as pd
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data
from src.visualizations import (
    create_candlestick_chart,
    create_moving_average_chart,
    create_daily_returns_histogram,
    create_volume_vs_close_scatter,
    create_high_low_chart,
    create_rsi_chart,
)

# IMPORTANTE: Importamos el motor de simulación
from src.mini_platform import run_simulation

st.set_page_config(page_title="Financial Architect Dashboard", layout="wide")

# Sidebar
st.sidebar.title("🛠️ Configuración")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper()
ma_window = st.sidebar.slider("Ventana Media Móvil (SMA)", 5, 200, 50)

st.title(f"🏛️ Arquitecto Financiero: {ticker}")
st.markdown("---")

if ticker:
    data = fetch_stock_data(ticker)

    if data.empty:
        st.error("Error: No se encontraron datos para el ticker ingresado.")
    else:
        # Preparación de datos
        data = data.reset_index()
        data["Date"] = pd.to_datetime(data["Date"]).dt.tz_localize(None)
        data = process_data(data, ma_window)

        # --- SECCIÓN 1: MÉTRICAS (KPIs) ---
        last_price = data["Close"].iloc[-1]
        last_ret = data["Daily Return"].iloc[-1] * 100
        vol = data["Volatility"].iloc[-1]

        m1, m2, m3 = st.columns(3)
        m1.metric("Precio Actual", f"${last_price:,.2f}")
        m2.metric("Cambio Diario", f"{last_ret:.2f}%", delta=f"{last_ret:.2f}%")
        m3.metric("Riesgo (Volatilidad)", f"{vol:.2%}")

        st.markdown("---")

        # --- SECCIÓN 2: PESTAÑAS ---
        # Añadimos la pestaña de Simulación de Bot
        t1, t2, t3, t4 = st.tabs(
            [
                "📊 Análisis Técnico",
                "⚠️ Riesgo y Volumen",
                "🤖 Trading Bot Simulation",
                "📑 Datos Brutos",
            ]
        )

        with t1:
            st.plotly_chart(
                create_candlestick_chart(data, ticker), use_container_width=True
            )
            st.plotly_chart(
                create_moving_average_chart(data, ticker, ma_window),
                use_container_width=True,
            )
            st.plotly_chart(create_rsi_chart(data), use_container_width=True)

        with t2:
            col_left, col_right = st.columns(2)
            with col_left:
                st.plotly_chart(
                    create_daily_returns_histogram(data), use_container_width=True
                )
            with col_right:
                st.plotly_chart(
                    create_volume_vs_close_scatter(data), use_container_width=True
                )
            st.plotly_chart(create_high_low_chart(data), use_container_width=True)

        with t3:
            st.subheader("Simulación de Estrategia Minimalista")
            st.info("Estrategia: COMPRA si Precio > SMA, VENDE si Precio < SMA.")

            # Botón para ejecutar el pipeline
            if st.button("🚀 Ejecutar Backtest"):
                ledger, final_pos, final_cash = run_simulation(data)

                # Resumen de resultados
                c1, c2 = st.columns(2)
                c1.success(f"**Posición Final:** {final_pos} unidades")
                c2.warning(f"**Balance de Caja Final:** ${final_cash:,.2f}")

                if ledger:
                    st.markdown("### Ledger (Últimos 10 trades)")
                    # Convertimos la lista de dataclasses en un DataFrame para mostrarlo mejor
                    ledger_df = pd.DataFrame([vars(t) for t in ledger])
                    st.dataframe(ledger_df.tail(10), use_container_width=True)
                else:
                    st.write("No se realizaron operaciones en este periodo.")

        with t4:
            st.dataframe(
                data.sort_values(by="Date", ascending=False), use_container_width=True
            )
