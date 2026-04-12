from dataclasses import dataclass


@dataclass
class Trade:
    t: any
    side: str
    qty: int
    fill: float
    fee: float
    reason: str


class TradingEngine:
    def __init__(self, max_qty=10, stop_loss_pct=0.05):
        self.max_qty = max_qty
        self.stop_loss_pct = stop_loss_pct  # 5% de pérdida máxima

    def strategy(self, px, sma, pattern, entry_price=None):
        """
        Lógica de decisión con protección de capital.
        """
        # 1. VERIFICACIÓN DE STOP LOSS (Prioridad máxima)
        if entry_price and px <= entry_price * (1 - self.stop_loss_pct):
            return "STOP_LOSS"

        # 2. SEÑAL DE VENTA POR TENDENCIA
        if px < sma:
            return "SELL"

        # 3. SEÑAL DE COMPRA POR CONFIRMACIÓN
        if px > sma and pattern != 0:
            return "BUY"

        return "HOLD"

    def execute(self, t, px, side, qty, reason="Signal"):
        # 2 bps de comisión
        fee = (2 / 10000) * (qty * px)
        return Trade(t, side, qty, round(px, 4), round(fee, 4), reason)


def run_simulation(df):
    engine = TradingEngine(stop_loss_pct=0.05)  # Configurable al 5%
    ledger, pos, cash = [], 0, 0.0
    entry_price = 0.0

    for i in range(len(df)):
        row = df.iloc[i]
        current_px = row["Close"]

        # Le pasamos el precio de entrada para que el motor calcule el riesgo
        side = engine.strategy(
            current_px,
            row["MA"],
            row["Pattern_Detected"],
            entry_price if pos > 0 else None,
        )

        # LÓGICA DE COMPRA
        if side == "BUY" and pos == 0:
            tr = engine.execute(
                row["Date"], current_px, "BUY", engine.max_qty, "Trend+Pattern"
            )
            pos += tr.qty
            entry_price = tr.fill
            cash -= tr.qty * tr.fill + tr.fee
            ledger.append(tr)

        # LÓGICA DE VENTA (Ya sea por Señal o por Stop Loss)
        elif (side in ["SELL", "STOP_LOSS"]) and pos > 0:
            reason = "Market Trend" if side == "SELL" else "Stop Loss Protection"
            tr = engine.execute(row["Date"], current_px, "SELL", pos, reason)
            cash += pos * tr.fill - tr.fee
            pos = 0
            entry_price = 0.0  # Reset precio de entrada
            ledger.append(tr)

    return ledger, pos, cash
