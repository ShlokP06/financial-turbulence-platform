from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    tables: list[str]

class TurbulenceResponse(BaseModel):
    date: str
    turbulence: float
    regime: str

class WeightsResponse(BaseModel):
    weights: dict[str, float]
    target_vol: float

class ForecastResponse(BaseModel):
    as_of: str
    horizons: list[int]
    values: list[float]

class RegimeRiskResponse(BaseModel):
    "Leading de-risk signal: probability turbulence exceeds its high trailing threshold within `horizon_days`."
    probability: float
    horizon_days: int
    as_of: str

class FeatureImportance(BaseModel):
    feature: str
    importance: float

class ExplainResponse(BaseModel):
    importances: list[FeatureImportance]

class AssetDriver(BaseModel):
    asset: str
    ret: float
    z: float

class NewsSource(BaseModel):
    title: str
    url: str
    published: str = ""

class WhyResponse(BaseModel):
    date: str
    turbulence: float
    regime: str
    drivers: list[AssetDriver]
    sources: list[NewsSource]
    explanation: str

class BacktestMetrics(BaseModel):
    ann_return: float
    ann_vol: float
    sharpe: float
    sortino: float
    max_drawdown: float
    cvar_95: float
    turnover: float

class EquityPoint(BaseModel):
    date: str
    strategy: float
    benchmark: float

class BacktestResponse(BaseModel):
    strategy: BacktestMetrics
    benchmark: BacktestMetrics
    equity: list[EquityPoint]
    rebalance_days: int
    cost_bps: float