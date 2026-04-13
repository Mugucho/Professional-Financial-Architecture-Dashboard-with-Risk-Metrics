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
    create_patterns_only_chart,
)
from src.mini_platform import (
    run_simulation,
    AlpacaExecutor,
    ALPACA_AVAILABLE,
    TradingEngine,
)

# 1. Configuración de la página (Debe ser la primera instrucción de Streamlit)
st.set_page_config(page_title="Financial Architect Dashboard", layout="wide")

# 2. Barra Lateral (Sidebar) - Configuración y Credenciales
st.sidebar.title("🏛️ Configuración")
ticker = st.sidebar.text_input("Símbolo Ticker", value="AAPL").upper()
ma_window = st.sidebar.slider("Ventana Media Móvil (SMA)", 5, 200, 50)
sl_input = st.sidebar.slider("Stop Loss %", 1, 20, 5) / 100

st.sidebar.markdown("---")
with st.sidebar.expander("🔑 Conexión Broker (Alpaca)"):
    api_key = st.text_input("API Key ID", type="password")
    secret_key = st.text_input("Secret Key", type="password")
    paper_mode = st.checkbox("Modo Paper Trading", value=True)

# 3. Encabezado Principal
st.title(f"Dashboard de Análisis y Ejecución: {ticker}")
st.markdown("---")

if ticker:
    # Obtención de datos desde Yahoo Finance
    data = fetch_stock_data(ticker)

    if not data.empty:
        # Procesamiento y limpieza de datos
        data = data.reset_index()
        if data["Date"].dt.tz is not None:
            data["Date"] = data["Date"].dt.tz_localize(None)

        data = process_data(data, ma_window)

        # KPIs Principales en la parte superior
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Precio Cierre", f"${data['Close'].iloc[-1]:.2f}")
        m2.metric("Retorno Diario", f"{data['Daily Return'].iloc[-1]*100:.2f}%")
        # Identificar dinámicamente la columna RSI calculada por pandas_ta
        rsi_col = [c for c in data.columns if "RSI" in c][-1]
        m3.metric("RSI (14)", f"{data[rsi_col].iloc[-1]:.2f}")
        m4.metric("Volatilidad Anual", f"{data['Volatility'].iloc[-1]:.2%}")

        # Organización por pestañas (Tabs)
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
            st.plotly_chart(create_candlestick_chart(data, ticker), width="stretch")
            st.plotly_chart(
                create_moving_average_chart(data, ticker, ma_window), width="stretch"
            )
            st.plotly_chart(create_rsi_chart(data), width="stretch")

        with t2:
            st.subheader("Análisis de Psicología de Velas")
            st.plotly_chart(create_patterns_only_chart(data, ticker), width="stretch")

        with t3:
            col_a, col_b = st.columns(2)
            with col_a:
                st.plotly_chart(create_daily_returns_histogram(data), width="stretch")
            with col_b:
                st.plotly_chart(create_high_low_chart(data), width="stretch")
            st.plotly_chart(create_volume_vs_close_scatter(data), width="stretch")

        with t4:
            st.subheader("Simulación y Ejecución")
            c1, c2 = st.columns(2)

            with c1:
                st.info("### 🧪 Backtest Histórico")
                if st.button("🚀 Iniciar Simulación"):
                    ledger, pos, cash = run_simulation(data, sl_input)
                    st.success(f"Balance Final Simulado: ${cash:,.2f}")
                    if ledger:
                        st.dataframe(
                            pd.DataFrame([vars(t) for t in ledger]), width="stretch"
                        )
                    else:
                        st.write("No se generaron trades en el periodo analizado.")

            with c2:
                st.warning("### ⚡ Operativa Real (Alpaca)")
                if not ALPACA_AVAILABLE:
                    st.error(
                        "Librería 'alpaca-py' no detectada. Instálala para operar."
                    )
                else:
                    # Mecanismo de seguridad con confirmación
                    confirmar_envio = st.checkbox(
                        "Habilitar envío de órdenes a mercado"
                    )

                    if st.button(
                        "Enviar Señal Actual a Alpaca", disabled=not confirmar_envio
                    ):
                        if api_key and secret_key:
                            try:
                                executor = AlpacaExecutor(
                                    api_key, secret_key, paper_mode
                                )
                                engine = TradingEngine(stop_loss_pct=sl_input)
                                last_row = data.iloc[-1]

                                # Evaluar estrategia con el último dato disponible
                                signal = engine.strategy(
                                    last_row["Close"],
                                    last_row["MA"],
                                    last_row["Pattern_Detected"],
                                )

                                if signal == "BUY":
                                    res = executor.place_order(ticker, 1, "BUY")
                                    st.success(
                                        f"ORDEN ENVIADA: Compra de 1 {ticker}. ID: {res.id}"
                                    )
                                elif signal == "SELL":
                                    res = executor.place_order(ticker, 1, "SELL")
                                    st.error(
                                        f"ORDEN ENVIADA: Venta de 1 {ticker}. ID: {res.id}"
                                    )
                                else:
                                    st.info(
                                        "No hay señal de entrada activa en este momento."
                                    )
                            except Exception as e:
                                st.error(f"Error de conexión o API: {e}")
                        else:
                            st.error(
                                "Por favor, ingresa tus credenciales en el panel lateral."
                            )

                    if not confirmar_envio:
                        st.caption(
                            "ℹ️ Activa la casilla de arriba para habilitar el botón de envío."
                        )

        with t5:
            st.dataframe(data.tail(100), width="stretch")
    else:
        st.error(f"Error: No se encontraron datos para {ticker}. Revisa el símbolo.")
