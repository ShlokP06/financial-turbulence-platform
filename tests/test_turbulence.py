import numpy as np
import pandas as pd
from turballoc.signals.turbulence import turbulence_index
from turballoc.signals.regime import classify_regime, turbulent_days, Regime

def _make_returns(n = 400, k = 4, seed = 0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2018-01-01", periods=n, name="date")
    cols = [f"A{i}" for i in range(k)]
    return pd.DataFrame(rng.normal(0, 0.01, size=(n, k)), index=idx, columns=cols)

def test_turbulence_nonnegative():
    turb = turbulence_index(_make_returns(), window=126, min_periods=60)
    assert (turb.dropna() >= 0).all()

def test_turbulence_index_alignment():
    rets = _make_returns()
    turb = turbulence_index(rets, window=126, min_periods=60)
    assert turb.index.equals(rets.index)
    assert turb.name == "turbulence"

def test_turbulence_spikes_on_shock():
    rets = _make_returns()
    shock_day = rets.index[-1]
    rets.loc[shock_day] = 0.2  # all assets jump 20% on one day
    turb = turbulence_index(rets, window=126, min_periods=60)
    assert turb.loc[shock_day] > turb.dropna().median() * 5

def test_classify_regime_labels():
    turb = turbulence_index(_make_returns(), window=126, min_periods=60)
    regime = classify_regime(turb, window=126, min_periods=60)
    assert set(regime.dropna().unique()) <= {Regime.CALM, Regime.NORMAL, Regime.TURBULENT}

def test_turbulent_days_mask_is_bool():
    turb = turbulence_index(_make_returns(), window=126, min_periods=60)
    regime = classify_regime(turb, window=126, min_periods=60)
    mask = turbulent_days(regime)
    assert mask.dtype == bool