from dataclasses import dataclass
import pandas as pd


@dataclass
class Trade:
    t: any
    side: str
    qty: int
    fill: float
    fee: float


class TradingEngine:
    def __init__(self, slip_bps=5, fee_bps=2, max_qty=10):
        self.slip_bps = slip_bps
        self.fee_bps = fee_bps
        self.max_qty = max_qty

    def strategy(self, current_px, sma):
        return "BUY" if current_px > sma else "SELL"

    def risk(self, side):
        # Aquí es donde conectas con tu propósito de proteger el capital
        return self.max_qty if side == "BUY" else 0

    def execute(self, time, px, side, qty):
        slip = (self.slip_bps / 10_000) * px
        fill = px + slip if side == "BUY" else px - slip
        fee = (self.fee_bps / 10_000) * (qty * fill)
        return Trade(time, side, qty, round(fill, 4), round(fee, 4))


def run_simulation(df):
    """Integra el pipeline con los datos del dashboard."""
    engine = TradingEngine()
    ledger, pos, cash = [], 0, 0.0

    # Iteramos sobre el DataFrame procesado
    for i in range(len(df)):
        current_px = df["Close"].iloc[i]
        sma = df["MA"].iloc[i]
        time = df["Date"].iloc[i]

        side = engine.strategy(current_px, sma)
        qty = engine.risk(side)

        if qty > 0:
            tr = engine.execute(time, current_px, side, qty)
            pos += qty
            cash -= qty * tr.fill + tr.fee
            ledger.append(tr)

    return ledger, pos, cash
