from pathlib import Path
import numpy as np
import pandas as pd
from turballoc.allocation.strategy import turbulence_managed_weights
from turballoc.config import settings
from turballoc.forecast.dataset import Horizons, build_feature_frame
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def latest_turbulence(store):
    df = store.read("turbulence").dropna(subset = ["turbulence"])
    if df.empty:
        return None
    row = df.iloc[-1]
    return {
        "date": df.index[-1].date().isoformat(),
        "turbulence": float(row["turbulence"]),
        "regime": str(row["regime"])
    }

def turbulence_history(store, limit = 504):
    df = store.read("turbulence").dropna(subset = ["turbulence"]).tail(limit)
    return [
        {
            "date": idx.date().isoformat(),
            "turbulence": float(row["turbulence"]),
            "regime": str(row["regime"]),
        }
        for idx, row in df.iterrows()
    ]

def compute_weights(store, lookback = 252, target_vol = 0.07, momentum = "continuous"):
    "Latest turbulence-managed weights (min-variance + vol-target + turbulence overlay + momentum tilt)."
    returns = store.read("returns").dropna(how = "any")
    if "turbulence" in store.list_tables():
        turb = store.read("turbulence").dropna(subset = ["turbulence"])["turbulence"]
    else:
        turb = pd.Series(dtype = float)
    return turbulence_managed_weights(returns.iloc[-lookback:], turb,
                                      target_vol = target_vol, momentum = momentum)

def run_backtest(store, lookback = 252, rebalance = 21, cost = 0.001, risk_aversion = 2.5,
                 momentum = "continuous"):
    "Walk-forward backtest of the turbulence-managed strategy (with momentum tilt) vs equal-weight."
    from turballoc.backtest.engine import run_strategy_backtest
    return run_strategy_backtest(store, lookback = lookback, rebalance = rebalance,
                                 cost = cost, momentum = momentum)


# Lazily load the forecast checkpoint once and reuse it; reload if the file changes.
_model_cache = {}

def _load_forecast_model():
    path = Path(settings.forecast_ckpt_path)
    if not path.exists():
        return None
    key = (str(path), path.stat().st_mtime)
    if key not in _model_cache:
        from turballoc.forecast.predict import load_model
        _model_cache.clear()
        _model_cache[key] = load_model(str(path))
        logger.info("Loaded forecast checkpoint %s", path)
    return _model_cache[key]

def forecast_latest(store):
    "Latest multi-horizon turbulence forecast, or None if no checkpoint / not enough history."
    bundle = _load_forecast_model()
    if bundle is None:
        return None
    model, ckpt = bundle
    features, _ = build_feature_frame(store)
    lookback = ckpt["lookback"]
    if len(features) < lookback or features.shape[1] != ckpt["n_features"]:
        return None
    from turballoc.forecast.predict import forecast as run_forecast
    values = run_forecast(model, features, lookback=lookback, ckpt=ckpt)
    return {
        "as_of": features.index[-1].date().isoformat(),
        "horizons": list(Horizons),
        "values": [float(v) for v in values],
    }

def latest_regime_risk(store, k = 10):
    "Latest forward-turbulence exceedance probability (leading de-risk signal), or None if too little history."
    from turballoc.forecast.exceedance import latest_exceedance_probability

    prob = latest_exceedance_probability(store, k = k)
    if prob is None:
        return None
    turb = store.read("turbulence").dropna(subset = ["turbulence"])
    as_of = turb.index[-1].date().isoformat() if not turb.empty else ""
    return {"probability": prob, "horizon_days": k, "as_of": as_of}

def explain_importance(store, horizon = 7, max_features = 12):
    "Global feature importance for turbulence at +`horizon` days via a gradient-boosted surrogate."
    features, target = build_feature_frame(store)
    y = target.shift(-horizon).dropna()
    X = features.loc[y.index]
    if len(X) < 50:
        return None

    from sklearn.ensemble import GradientBoostingRegressor

    surrogate = GradientBoostingRegressor(random_state = settings.random_seed)
    surrogate.fit(X.to_numpy(), y.to_numpy())
    ranked = pd.Series(surrogate.feature_importances_, index = X.columns).sort_values(ascending = False)
    return [{"feature": str(k), "importance": float(v)} for k, v in ranked.head(max_features).items()]

def explain_turbulence_day(store, date):
    "Grounded LLM explanation of why turbulence was elevated on `date` (news + asset moves)."
    from turballoc.explain.news_explainer import explain_day
    return explain_day(store, date)


def explain_turbulence_day_basic(store, date):
    "Keyless, data-driven explanation: turbulence value, regime, and the driving asset moves."
    from turballoc.explain.news_explainer import asset_drivers

    turb = store.read("turbulence")
    ts = pd.Timestamp(date)
    if ts not in turb.index or pd.isna(turb.loc[ts, "turbulence"]):
        raise ValueError(f"no turbulence for {date}")
    value = float(turb.loc[ts, "turbulence"])
    regime = str(turb.loc[ts, "regime"])
    drivers = asset_drivers(store, ts)
    moves = ", ".join(f"{d['asset']} ({d['ret'] * 100:+.1f}%, {d['z']:+.1f}σ)" for d in drivers)
    explanation = (
        f"On {date} the turbulence index read {value:.1f} (a {regime} regime). The reading was "
        f"driven by unusually large, jointly improbable moves in {moves} — a cross-asset "
        f"dislocation relative to the recent covariance regime. Set GROQ_API_KEY and "
        f"TAVILY_API_KEY to enrich this with news-grounded LLM narration."
    )
    return {"date": str(date), "turbulence": value, "regime": regime,
            "drivers": drivers, "sources": [], "explanation": explanation}

