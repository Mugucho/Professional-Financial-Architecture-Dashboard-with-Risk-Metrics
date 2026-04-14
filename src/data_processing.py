import pandas as pd
import pandas_ta as ta

def process_data(df, ma_window):
    """
    Procesa indicadores técnicos usando pandas_ta.
    Optimizado para despliegue en iPad y Nube.
    """
    # Aseguramos que los datos sean numéricos
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')

    # 1. RSI (Relative Strength Index)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # 2. SMA (Simple Moving Average)
    df['SMA'] = ta.sma(df['Close'], length=ma_window)
    
    # 3. Retornos Diarios
    df['Daily Return'] = df['Close'].pct_change()
    
    # 4. Análisis de Volumen Relativo
    df['Vol_Avg'] = ta.sma(df['Volume'], length=20)
    df['Rel_Vol'] = df['Volume'] / df['Vol_Avg']
    
    # Rellenar ceros para evitar errores de PyArrow en Streamlit
    df = df.fillna(0)
    
    return df

def calculate_support_resistance(df, window=50):
    """
    Cálculo de niveles dinámicos para la arquitectura de mercado.
    """
    df['Support_Level'] = df['Low'].rolling(window=window).min()
    df['Resistance_Level'] = df['High'].rolling(window=window).max()
    return df