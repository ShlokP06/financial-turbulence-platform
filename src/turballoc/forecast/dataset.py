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
        Y.append(tgt[t+h] for h in horizons)
        dates.append(features.index[t])
    X = np.asarray(X, dtype = "float32")
    Y = np.asarray(Y, dtype="float32")
    logger.info("Built %d windows (looback=%d, horizons=%s)", len(X), lookback, list(horizons))
    return X, Y, pd.DatetimeIndex(dates, name = "date")

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
    