# financial-turbulence-platform

AI-powered detection of **financial turbulence** and **dynamic, explainable asset
reallocation** across asset classes.

The system ingests multi-source market data, computes a turbulence signal, forecasts
near-term market conditions, reallocates a portfolio to manage risk, and serves it all
behind a low-latency API — with model explanations.

> **Status:** in progress. Ingestion, NLP sentiment, the turbulence/regime signal,
> risk clustering, forecasting, allocation (Black-Litterman + Bayesian optimization),
> and backtesting are implemented with unit tests per module. Not yet done: the RL
> allocation agent, SHAP/counterfactual explainability, the frontend, and end-to-end
> integration testing — see the roadmap below for exactly what's left.

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

| Path | Purpose | Status |
| --- | --- | --- |
| `src/turballoc/ingest/` | ETL: structured (market, macro, credit) + unstructured (news, reddit) | done |
| `src/turballoc/nlp/` | FinBERT sentiment features | done |
| `src/turballoc/signals/` | Turbulence index + regime classification | done |
| `src/turballoc/clustering/` | Unsupervised risk-behavior profiles | done |
| `src/turballoc/forecast/` | LSTM-CNN market-condition forecasting | done |
| `src/turballoc/allocation/` | Black-Litterman + Bayesian optimization | done; RL agent not started |
| `src/turballoc/backtest/` | Walk-forward, leakage-free backtest + risk metrics | done |
| `src/turballoc/explain/` | SHAP + counterfactuals | not started |
| `src/turballoc/serve/` | FastAPI inference API | done |
| `tests/` | pytest, one file per module | in place for ingest, nlp, turbulence, clustering, forecast, allocation, backtest |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,rl]"
cp .env.example .env                                 # fill in API keys
```

## Build roadmap

0. Scaffold — done
1. Structured ETL (market + macro + credit proxy → feature store) — done
2. Unstructured ingestion + FinBERT sentiment — done
3. Turbulence index + regime classification — done
4. Risk-behavior clustering — done
5. LSTM-CNN forecasting — done
6. Allocation: Black-Litterman + Bayesian opt — done; RL agent — not started
7. Explainability: SHAP + counterfactuals — not started
8. Serving: FastAPI low-latency endpoints — done
9. Frontend — not started, separate effort
10. Hardening: end-to-end integration tests, Docker, docs — in progress

## License

MIT — see [LICENSE](LICENSE).
