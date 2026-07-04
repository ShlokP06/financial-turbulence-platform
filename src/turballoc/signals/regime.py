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
    ok = lo.notna() & hi.notna() & turbulence.notna()
    # Plain string labels via boolean indexing. (Series.mask with the str-Enum routes through
    # numpy.where, which coerces the member to a fixed-width string and truncates it.)
    regime = pd.Series(pd.NA, index = turbulence.index, dtype = object, name = "regime")
    regime[ok] = Regime.NORMAL.value
    regime[ok & (turbulence >= hi)] = Regime.TURBULENT.value
    regime[ok & (turbulence < lo)] = Regime.CALM.value
    return regime

def turbulent_days(regime):
    "Return boolean mask of turbulent days."
    return (regime == Regime.TURBULENT).fillna(False).astype(bool)