import time
import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from turballoc.config import settings
from turballoc.ingest.store import FeatureStore
from turballoc.logging_utils import get_logger
from turballoc.serve import service
from turballoc.serve.schemas import (BacktestResponse, ExplainResponse, ForecastResponse,
                                     HealthResponse, RegimeRiskResponse, TurbulenceResponse,
                                     WeightsResponse, WhyResponse)

logger = get_logger(__name__)

app = FastAPI(title = "turballoc",
              description = "Financial Turbulence Detection and Dynamic Asset Reallocation")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_methods = ["GET"],
    allow_headers = ["*"],
    expose_headers = ["X-Process-Time-ms"],
)

def get_store():
    return FeatureStore()

@app.middleware("http")
async def add_process_time(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response

@app.get("/health", response_model = HealthResponse)
def health(store = Depends(get_store)):
    "Liveness check and the feature tables currently available."
    return HealthResponse(status = "ok", tables = store.list_tables())

@app.get("/turbulence/latest", response_model = TurbulenceResponse)
def turbulence_latest(store = Depends(get_store)):
    "Most recent turbulence value and regime label."
    latest = service.latest_turbulence(store)
    if latest is None:
        raise HTTPException(status_code=404, detail = "no turbulence data; run build_turbulence_feature")
    return TurbulenceResponse(**latest)

@app.get("/turbulence/history", response_model = list[TurbulenceResponse])
def turbulence_history(limit: int = 504, store = Depends(get_store)):
    "Recent turbulence time series - most recent `limit` observations."
    return service.turbulence_history(store, limit = limit)

@app.get("/weights", response_model = WeightsResponse)
def weights(target_vol: float = 0.07, lookback: int = 252, store = Depends(get_store)):
    "Latest weights; `target_vol` is the risk dial — lower targets hold more cash."
    try:
        w = service.compute_weights(store, lookback = lookback, target_vol = target_vol)
    except KeyError:
        raise HTTPException(status_code=404, detail="no returns table; run ETL first.")
    return WeightsResponse(weights = {k: float(v) for k, v in w.items()}, target_vol=target_vol)

@app.get("/forecast", response_model = ForecastResponse)
def forecast(store = Depends(get_store)):
    "Latest multi-horizon (7/30/90-day) turbulence forecast from the trained LSTM-CNN."
    out = service.forecast_latest(store)
    if out is None:
        raise HTTPException(status_code=503, detail="no forecast model; run scripts/train_forecast.py")
    return out

@app.get("/regime/risk", response_model = RegimeRiskResponse)
def regime_risk(store = Depends(get_store)):
    "Leading de-risk signal: probability turbulence exceeds its high trailing threshold within 10 days (walk-forward logistic exceedance model)."
    try:
        out = service.latest_regime_risk(store)
    except KeyError:
        raise HTTPException(status_code=404, detail="need returns + turbulence + credit tables; run ETL + build_turbulence_feature")
    if out is None:
        raise HTTPException(status_code=503, detail="not enough history for the exceedance model yet")
    return out

@app.get("/backtest", response_model = BacktestResponse)
def backtest(rebalance: int = 21, cost: float = 0.001, risk_aversion: float = 2.5, store = Depends(get_store)):
    "Walk-forward backtest (no look-ahead) of the turbulence-managed min-variance strategy vs equal-weight."
    try:
        return service.run_backtest(store, rebalance=rebalance, cost=cost, risk_aversion=risk_aversion)
    except KeyError:
        raise HTTPException(status_code=404, detail="need returns + turbulence tables; run ETL + build_turbulence_feature")

@app.get("/turbulence/why", response_model = WhyResponse)
def turbulence_why(date: str, store = Depends(get_store)):
    "Why turbulence was elevated on `date`: data-driven asset drivers, enriched with Groq+Tavily news narration when those keys are set."
    try:
        if settings.groq_api_key and settings.tavily_api_key:
            return service.explain_turbulence_day(store, date)
        return service.explain_turbulence_day_basic(store, date)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except httpx.HTTPError as exc:
        logger.warning("turbulence/why upstream error: %s; using data-driven fallback", exc)
        try:
            return service.explain_turbulence_day_basic(store, date)
        except ValueError as e2:
            raise HTTPException(status_code=404, detail=str(e2))

@app.get("/explain", response_model = ExplainResponse)
def explain(store = Depends(get_store)):
    "Global feature importance for the turbulence forecast (gradient-boosted surrogate over live features)."
    try:
        importances = service.explain_importance(store)
    except KeyError:
        raise HTTPException(status_code=404, detail="no feature data; run ETL + build_turbulence_feature")
    if importances is None:
        raise HTTPException(status_code=503, detail="not enough history to explain yet")
    return ExplainResponse(importances=importances)
