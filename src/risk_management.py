def drawdown_gate(account, max_drawdown_pct=-0.02):
    """
    Compuerta 1: Bloquea el sistema si la pérdida diaria supera el límite (-2%).
    """
    daily_pl = (float(account.equity) - float(account.last_equity)) / float(
        account.last_equity
    )
    return daily_pl >= max_drawdown_pct, daily_pl


def exposure_gate(account, price, max_portfolio_pct=0.10):
    """
    Compuerta 2: Calcula el tamaño máximo de posición permitido (10% del portafolio).
    """
    return int((float(account.equity) * max_portfolio_pct) / price)


def reconciliation_gate(tc, ticker):
    """
    Compuerta 3: Verifica si ya existe una posición abierta para evitar duplicados.
    """
    try:
        return float(tc.get_open_position(ticker).qty)
    except:
        return 0.0
