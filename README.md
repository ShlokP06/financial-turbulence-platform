# financial-turbulence-platform

AI-powered detection of **financial turbulence** and **dynamic, explainable asset
reallocation** across asset classes.

The system ingests multi-source market data, computes a turbulence signal, forecasts
near-term market conditions, reallocates a portfolio to manage risk, and serves it all
behind a low-latency API — with model explanations.

> **Status:** scaffold. Directory structure and config are in place; all `.py` logic is
> implemented phase by phase (see the build roadmap below). Not yet functional.

## Core idea

The **turbulence index** is the Mahalanobis distance of current multi-asset returns from
their rolling historical mean and covariance (Kritzman & Li, 2010, *Skulls, Financial
Turbulence, and Risk Management*). High turbulence = statistically abnormal,
correlation-breaking markets that historically precede drawdowns. This signal drives regime
classification, allocation views, and scenario simulations.

## Architecture

```
ingest ─┬─ market (yfinance)     ┐
        ├─ macro (FRED)          │
        ├─ credit (CDS proxy)    ├─► feature store (parquet/DuckDB) ─► signals (turbulence + regime)
        ├─ news (GDELT/NewsAPI)  │            │                              │
        └─ reddit (PRAW)         ┘            ▼                              ▼
                                          nlp (FinBERT)                clustering / forecast (LSTM-CNN)
                                                                              │
                                                          allocation (Black-Litterman + Bayesian opt + RL)
                                                                              │
                                            backtest (walk-forward, no-leakage) ─► explain (SHAP)
                                                                              │
                                                              serve (FastAPI, low-latency)
```

The frontend (dashboards, heatmaps, scenario simulations) is a **separate, later** effort —
deliberately not included here.

## Layout

| Path | Purpose |
| --- | --- |
| `src/turballoc/ingest/` | ETL: structured (market, macro, credit) + unstructured (news, reddit) |
| `src/turballoc/nlp/` | FinBERT sentiment features |
| `src/turballoc/signals/` | Turbulence index + regime classification |
| `src/turballoc/clustering/` | Unsupervised risk-behavior profiles |
| `src/turballoc/forecast/` | LSTM-CNN + attention market-condition forecasts |
| `src/turballoc/allocation/` | Black-Litterman, Bayesian optimization, RL agent |
| `src/turballoc/backtest/` | Walk-forward, leakage-free backtest + risk metrics |
| `src/turballoc/explain/` | SHAP + counterfactuals |
| `src/turballoc/serve/` | FastAPI inference API |
| `tests/` | pytest (incl. backtest leakage guard) |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,rl]"
cp .env.example .env                                 # fill in API keys
```

## Build roadmap

0. Scaffold ✅
1. Structured ETL (market + macro + credit proxy → feature store)
2. Unstructured ingestion + FinBERT sentiment
3. Turbulence index + regime classification
4. Risk-behavior clustering
5. LSTM-CNN + attention forecasting (7/30/90-day)
6. Allocation: Black-Litterman + Bayesian opt, then RL agent
7. Explainability: SHAP + counterfactuals
8. Serving: FastAPI low-latency endpoints
9. Frontend (separate, later)
10. Hardening: validation protocols, full tests, Docker, docs

## License

MIT — see [LICENSE](LICENSE).
