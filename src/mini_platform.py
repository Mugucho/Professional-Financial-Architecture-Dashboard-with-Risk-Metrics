from dataclasses import dataclass
import pandas as pd

# Intentamos importar Alpaca de forma segura
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce

    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False


@dataclass
class Trade:
    t: any
    side: str
    qty: int
    fill: float
    fee: float
    reason: str


class AlpacaExecutor:
    """Módulo de ejecución para Alpaca (Paper Trading)"""

    def __init__(self, api_key, secret_key, paper=True):
        if not ALPACA_AVAILABLE:
            raise ImportError("Librería 'alpaca-py' no instalada.")
        self.client = TradingClient(api_key, secret_key, paper=paper)

    def place_order(self, symbol, qty, side):
        try:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side == "BUY" else OrderSide.SELL,
                time_in_force=TimeInForce.GTC,
            )
            return self.client.submit_order(order_data=order_data)
        except Exception as e:
            return f"Error: {e}"


class TradingEngine:
    """Cerebro lógico para decisiones de trading."""

    def __init__(self, max_qty=10, stop_loss_pct=0.05):
        self.max_qty = max_qty
        self.stop_loss_pct = stop_loss_pct

    def strategy(self, px, sma, pattern, entry_price=None):
        # 1. Protección de Stop Loss
        if entry_price and px <= entry_price * (1 - self.stop_loss_pct):
            return "STOP_LOSS"
        # 2. Señal de Compra (Precio > Media + Patrón Alcista)
        if px > sma and pattern != 0:
            return "BUY"
        # 3. Señal de Venta (Precio < Media)
        if px < sma:
            return "SELL"
        return "HOLD"

    def execute_virtual(self, t, px, side, qty, reason="Signal"):
        """Simula una ejecución con comisiones para el backtest."""
        fee = (2 / 10000) * (qty * px)  # 2 bps
        return Trade(t, side, qty, round(px, 4), round(fee, 4), reason)


def run_simulation(df, sl_pct=0.05):
    """
    ESTA ES LA FUNCIÓN QUE FALTABA.
    Ejecuta el backtest histórico sobre el DataFrame.
    """
    engine = TradingEngine(stop_loss_pct=sl_pct)
    ledger, pos, cash, entry_price = [], 0, 0.0, 0.0

    for i in range(len(df)):
        row = df.iloc[i]
        side = engine.strategy(
            row["Close"],
            row["MA"],
            row["Pattern_Detected"],
            entry_price if pos > 0 else None,
        )

        # Lógica de Compra
        if side == "BUY" and pos == 0:
            tr = engine.execute_virtual(
                row["Date"], row["Close"], "BUY", engine.max_qty, "Trend+Pattern"
            )
            pos += tr.qty
            entry_price = tr.fill
            cash -= tr.qty * tr.fill + tr.fee
            ledger.append(tr)

        # Lógica de Venta o Stop Loss
        elif (side in ["SELL", "STOP_LOSS"]) and pos > 0:
            reason = "Market Trend" if side == "SELL" else "Stop Loss"
            tr = engine.execute_virtual(row["Date"], row["Close"], "SELL", pos, reason)
            cash += pos * tr.fill - tr.fee
            pos = 0
            entry_price = 0.0
            ledger.append(tr)

    return ledger, pos, cash
