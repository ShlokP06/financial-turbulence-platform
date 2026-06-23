import time
from fastapi import Depends, FastAPI, HTTPException
from turballoc.ingest.store import FeatureStore
from turballoc.logging_utils import get_logger
from turballoc.serve import service
from turballoc.serve.schemas import HealthResponse, TurbulenceResponse, WeightsResponse

logger = get_logger(__name__)

app = FastAPI(title = "turballoc",
              description = "Financial Turbulence Detection and Dynamic Asset Reallocation")

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

@app.get("/weights", response_model = WeightsResponse)
def weights(risk_aversion: float = 2.5, lookback: int = 252, store = Depends(get_store)):
    try:
        w = service.compute_weights(store, lookback = lookback, risk_aversion = risk_aversion)
    except KeyError:
        raise HTTPException(status_code=404, detail="no returns table; run ETL first.")
    return WeightsResponse(weights = {k: float(v) for k, v in w.items()}, risk_aversion=risk_aversion)
