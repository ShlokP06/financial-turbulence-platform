import numpy as np
import pandas as pd
from turballoc.backtest.metrics import summary
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def walk_forward_backtest(returns, weight_fn, lookback = 252, rebalance = 21, cost = 0.001):
    """
    Walk-forward backtest with no lookahead. 
    At each rebalance step, weight_fn sees ONLY returns.iloc[:i] and
    returns target weights, applied to forward returns until the next
    rebalance. A linear transaction cost is charged on L1 weight turnover
    at each rebalance.
    
    Returns (portfolio_returns, weight_log, stats).
    """

    dates = returns.index
    weights = pd.Series(np.zeros(returns.shape[1]), index = returns.columns)
    port = pd.Series(0.0, index = dates)
    weight_log = {}
    
    for i in range(lookback, len(dates)):
        if (i - lookback) % rebalance == 0:
            target = weight_fn(returns.iloc[:i])    #only past, no leakage
            target = target.reindex(returns.columns).fillna(0.0)
            turnover = (target - weights).abs().sum()
            port.iloc[i] = -cost * turnover
            weights = target
            weight_log[dates[i]] = weights
        port.iloc[i] += float((weights * returns.iloc[i]).sum())
    port = port.iloc[lookback:]
    stats = summary(port)
    logger.info("Backtest: sharpe = %.2f maxDD = %.1f%%", stats["sharpe"], 100 * stats["max_drawdown"])
    return port, pd.DataFrame(weight_log).T, stats