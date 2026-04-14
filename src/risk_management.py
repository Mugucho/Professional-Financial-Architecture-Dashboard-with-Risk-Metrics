# Archivo: src/risk_management.py


def drawdown_gate(account, max_drawdown_pct=-0.02):
    """
    COMPUERTA 1: Freno de Emergencia (Drawdown Gate).
    Objetivo: Proteger la cuenta de días catastróficos.
    Compara la equidad actual con la equidad del día anterior.
    Si la pérdida supera el límite (ej. -2%), bloquea el sistema.
    """
    equity = float(account.equity)
    last_equity = float(account.last_equity)
    daily_pl_pct = (equity - last_equity) / last_equity

    # Es seguro operar si el P/L es mayor al límite máximo de pérdida
    is_safe = daily_pl_pct >= max_drawdown_pct
    return is_safe, daily_pl_pct


def exposure_gate(account, current_price, max_portfolio_pct=0.10):
    """
    COMPUERTA 2: Límite de Exposición (Exposure Gate).
    Objetivo: Evitar apostar todo el capital a un solo caballo.
    Calcula cuántas acciones puedes comprar como máximo para que
    ninguna operación supere el 10% (o el % que elijas) de tu capital total.
    """
    max_capital_for_trade = float(account.equity) * max_portfolio_pct
    # Calculamos la cantidad máxima de acciones que podemos comprar con ese capital
    max_qty = int(max_capital_for_trade / current_price)
    return max_qty


def reconciliation_gate(tc, ticker):
    """
    COMPUERTA 3: Reconciliación y Memoria (Reconciliation Gate).
    Objetivo: Idempotencia. Prevenir compras duplicadas por error.
    En lugar de usar una variable en memoria que se borra al reiniciar,
    le preguntamos a la base de datos de Alpaca si ya tenemos esta acción.
    """
    try:
        # Preguntamos a Alpaca por la posición actual
        position = tc.get_open_position(symbol_or_asset_id=ticker)
        return float(position.qty)
    except Exception:
        # Si Alpaca lanza un error, significa que no tenemos acciones de este ticker
        return 0.0
