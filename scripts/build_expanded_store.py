"""Build the expanded-universe feature store.

Fetches the expanded ticker set (core 10 + BIL/TIP/USO/EMB), writes returns and a recomputed
turbulence index to `data/processed/features_expanded.duckdb`, and copies the credit table from
the core store (for forecast features). The core `features.duckdb` is left untouched so the
validated 10-asset pipeline stays intact.

Usage: python scripts/build_expanded_store.py
"""
from __future__ import annotations

from pathlib import Path

from turballoc.ingest.market import expanded, fetch_prices, to_returns
from turballoc.ingest.store import FeatureStore
from turballoc.signals.turbulence import build_turbulence_feature

CORE = Path("data/processed/features.duckdb")
EXPANDED = Path("data/processed/features_expanded.duckdb")


def main() -> None:
    prices = fetch_prices(expanded, start="2010-01-01")
    returns = to_returns(prices, kind="log").reindex(columns=list(expanded)).dropna(how="any")
    returns.index.name = "date"

    store = FeatureStore(EXPANDED)
    store.write("returns", returns)
    build_turbulence_feature(window=252, store=store)

    core = FeatureStore(CORE)
    if "credit" in core.list_tables():
        store.write("credit", core.read("credit"))

    print(f"Expanded store: {EXPANDED}")
    print(f"  returns: {returns.shape[0]} rows x {returns.shape[1]} assets "
          f"({returns.index.min().date()} -> {returns.index.max().date()})")
    print(f"  tables: {store.list_tables()}")


if __name__ == "__main__":
    main()
