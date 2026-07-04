import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

Horizons = (7, 30, 90)

def make_windows(features, target, lookback = 60, horizons = Horizons):
    "Build sliding window sequences"
    feats = features.to_numpy(dtype="float32")
    tgt = target.to_numpy(dtype="float32")
    max_h = max(horizons)
    n = len(features)
    X, Y, dates = [], [], []
    for t in range(lookback-1, n-max_h):
        X.append(feats[t - lookback + 1: t+1])
        Y.append([tgt[t+h] for h in horizons])
        dates.append(features.index[t])
    X = np.asarray(X, dtype = "float32")
    Y = np.asarray(Y, dtype="float32")
    logger.info("Built %d windows (lookback=%d, horizons=%s)", len(X), lookback, list(horizons))
    return X, Y, pd.DatetimeIndex(dates, name = "date")

def build_feature_frame(store):
    """Assemble the model's input features and turbulence target from the feature store.

    Features = asset returns + the turbulence level + any numeric macro/credit columns,
    date-aligned and forward-filled. The target is the (raw) turbulence level. Features are
    standardized so the conv/LSTM aren't dominated by the turbulence column's larger scale;
    the target stays in turbulence units so forecasts are directly interpretable. The training
    script and the /forecast endpoint both call this, so the inference window matches training.
    """
    tables = store.list_tables()
    if "returns" not in tables or "turbulence" not in tables:
        raise KeyError("need 'returns' and 'turbulence' tables; run ETL + build_turbulence_feature")

    frame = store.read("returns").copy()
    frame = frame.join(store.read("turbulence")[["turbulence"]], how="left")
    for name in ("credit", "macro"):
        if name in tables:
            frame = frame.join(store.read(name).select_dtypes("number"), how="left")

    frame = frame.ffill().dropna()
    # Turbulence is a Mahalanobis distance: strongly right-skewed with rare extreme spikes
    # (a near-singular trailing covariance can blow it up by orders of magnitude). Work in
    # log space so it neither dominates the standardized inputs nor wrecks the MSE target.
    frame["turbulence"] = np.log1p(frame["turbulence"])
    target = frame["turbulence"].copy()
    std = frame.std(ddof=0).replace(0, 1.0)
    features = (frame - frame.mean()) / std
    logger.info("Feature frame: %d rows x %d features", len(features), features.shape[1])
    return features, target

def time_split(n, train = 0.7, val = 0.15):
    "Chronological splits, allowing no future leakage"
    i_train = int(n*train)
    i_val = int(n*(train+val))
    return slice(0, i_train), slice(i_train, i_val), slice(i_val, n)

class SeqData(Dataset):
    def __init__(self, X, Y):
        self.X = torch.as_tensor(X, dtype = torch.float32)
        self.Y = torch.as_tensor(Y, dtype = torch.float32)

    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]
    