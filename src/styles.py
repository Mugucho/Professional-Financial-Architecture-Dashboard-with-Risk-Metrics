import streamlit as st


def apply_futuristic_design():
    st.markdown(
        """
        <style>
        /* Fondo general y fuentes */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0E1117;
            font-family: 'JetBrains+Mono', monospace;
        }

        /* Tarjetas (Containers) Estilo Glassmorphism */
        div[data-testid="stMetricValue"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 255, 163, 0.2);
            border-radius: 15px;
            padding: 15px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* Pestañas (Tabs) Futuristas */
        button[data-baseweb="tab"] {
            font-size: 14px !important;
            color: #808495 !important;
            border-radius: 10px 10px 0 0 !important;
            border: none !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #00FFA3 !important;
            background-color: rgba(0, 255, 163, 0.1) !important;
            border-bottom: 2px solid #00FFA3 !important;
        }

        /* Sidebar con estilo de consola de mando */
        [data-testid="stSidebar"] {
            background-color: #05070A;
            border-right: 1px solid rgba(0, 255, 163, 0.1);
        }

        /* Botones con brillo neón */
        .stButton>button {
            background-color: transparent;
            color: #00FFA3;
            border: 1px solid #00FFA3;
            border-radius: 20px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-weight: bold;
            letter-spacing: 2px;
        }
        .stButton>button:hover {
            background-color: #00FFA3;
            color: #0E1117;
            box-shadow: 0 0 20px rgba(0, 255, 163, 0.6);
        }

        /* Headers estilizados */
        h1, h2, h3 {
            color: #00FFA3 !important;
            text-shadow: 0 0 10px rgba(0, 255, 163, 0.3);
        }
        </style>
    """,
        unsafe_allow_html=True,
    )
