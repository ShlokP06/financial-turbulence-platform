"""Train the LSTM-CNN turbulence forecaster on whatever is in the feature store.

Assembles features with `build_feature_frame` (so they match what the /forecast endpoint
feeds at inference), trains, and saves a checkpoint to `settings.forecast_ckpt_path`
(default `checkpoints/forecast.pt`). Run after ETL + build_turbulence_feature, or after
seed_demo.py for a synthetic-data checkpoint:

    python scripts/train_forecast.py
"""

from pathlib import Path

from turballoc.config import settings
from turballoc.forecast.dataset import build_feature_frame
from turballoc.forecast.train import train_model
from turballoc.ingest.store import FeatureStore
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)


def main(lookback: int = 60, epochs: int = 30) -> None:
    store = FeatureStore()
    features, target = build_feature_frame(store)
    ckpt = Path(settings.forecast_ckpt_path)
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Training on %d rows x %d features -> %s", len(features), features.shape[1], ckpt)
    train_model(features, target, lookback=lookback, epochs=epochs, ckpt_path=str(ckpt))


if __name__ == "__main__":
    main()
