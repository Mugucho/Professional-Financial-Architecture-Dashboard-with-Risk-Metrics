# 🏛️ Financial Architect Dashboard

A professional-grade financial analysis environment built with **Python** and **Streamlit**. This project transitions from basic stock tracking to a robust decision-making tool focused on **risk assessment**, **market momentum**, and **modular software architecture**.

## 🎯 Project Purpose
The "Financial Architect" dashboard is designed to filter market noise and focus on high-value data. By integrating technical indicators with risk metrics, it provides a data-driven approach to investment analysis, aligning with the goal of long-term financial independence and professional technical mastery.

## 🛠️ Key Features
* **KPI Scoreboard:** Instant visualization of Current Price, Daily Change (%), and Annualized Volatility.
* **Technical Analysis Tab:** High-fidelity Candlestick charts, custom Moving Averages (MA), and the **RSI (Relative Strength Index)**.
* **Risk & Volume Tab:** Distribution analysis of daily returns and Volume-Price correlation.
* **Modular Architecture:** Clean separation of concerns using a `src/` directory for scalability.
* **Resilient Pipeline:** Automated data fetching via `yfinance` with integrated exception handling.

## 🏗️ Project Structure
```text
.
├── dashboard.py           # Main Streamlit application (UI & Layout)
├── README.md              # Project documentation
├── requirements.txt       # Necessary Python libraries
├── .gitignore             # Excludes venv and temporary files
└── src/                   # Source code directory
    ├── __init__.py        # Package initializer
    ├── data_fetcher.py    # Market data extraction logic
    ├── data_processing.py # Financial math & risk metrics
    └── visualizations.py  # Plotly-based professional charts
