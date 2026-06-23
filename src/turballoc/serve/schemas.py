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
    risk_aversion: float