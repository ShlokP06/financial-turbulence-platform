from enum import Enum
import pandas as pd
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

class Regime(str, Enum):
    CALM = "calm"
    NORMAL = "normal"
    TURBULENT = "turbulent"

def classify_regime(turbulence, window = 252, low = 0.3, high = 0.8, min_periods = 126):
    lo = turbulence.rolling(window, min_periods = min_periods).quantile(low)
    hi = turbulence.rolling(window, min_periods = min_periods).quantile(high)
    valid = lo.notna() & hi.notna()
    regime = pd.Series(Regime.NORMAL, index = turbulence.index, dtype = object, name = "regime")
    regime = regime.mask(valid & (turbulence >= hi), Regime.TURBULENT)
    regime = regime.mask(valid & (turbulence < lo), Regime.CALM)
    regime = regime.mask(turbulence.isna() | ~valid, pd.NA)
    return regime

def turbulent_days(regime):
    "Return boolean mask of turbulent days."
    return (regime == Regime.TURBULENT).fillna(False).astype(bool)