import numpy as np

TRADING_DAYS = 252

def annualized_return(returns, periods = TRADING_DAYS):
    "Geometric annualized return rom a series of periodic returns"
    n = len(returns)
    if n == 0:
        return 0.0
    growth = (1 + returns).prod()
    return growth ** (periods/n) - 1

def annualized_vol(returns, periods = TRADING_DAYS):
    return returns.std(ddof = 0) * np.sqrt(periods)

def sharpe_ratio(returns, rf = 0.0, periods = TRADING_DAYS):
    excess = returns - rf / periods
    sd = excess.std(ddof = 0)
    if sd == 0:
        return 0.0
    return np.sqrt(periods) * excess.mean() / sd

def sortino_ratio(returns, rf = 0.0, periods = TRADING_DAYS):
    "Similar to Sharpe, but penalizes only downside volatility"
    excess = returns - rf / periods
    downside = excess[excess < 0].std(ddof = 0)
    if downside == 0:
        return 0.0
    return np.sqrt(periods) * excess.mean() / downside

def max_drawdown(returns):
    "Worst peak-tovalley decline of the equity curve"
    equity = (1 + returns).cumprod()
    peak = equity.cummax()
    return float((equity / peak - 1).min())

def cvar(returns, alpha = 0.05):
    "Conditional Value-at-Risk: mean of the worst alpha-tail of periodic returns (a negative number)."
    if len(returns) == 0:
        return 0.0
    var = np.quantile(returns, alpha)
    tail = returns[returns <= var]
    return float(tail.mean()) if len(tail) else float(var)

def summary(returns):
    return {
        "ann_return": float(annualized_return(returns)),
        "ann_vol": float(annualized_vol(returns)),
        "sharpe": float(sharpe_ratio(returns)),
        "sortino": float(sortino_ratio(returns)),
        "max_drawdown": max_drawdown(returns),
        "cvar_95": cvar(returns, 0.05),
    }
