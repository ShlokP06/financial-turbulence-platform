import numpy as np
import pandas as pd
import torch
from turballoc.forecast.dataset import make_windows, time_split
from turballoc.forecast.model import LSTMCNN

def _make_frame(n = 300, f = 5, seed = 0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2018-01-01", periods=n, name="date")
    feats = pd.DataFrame(rng.normal(size=(n, f)), index=idx,
                         columns=[f"f{i}" for i in range(f)])
    target = pd.Series(rng.normal(size=n), index=idx, name="y")
    return feats, target

def test_make_windows_shapes():
    feats, target = _make_frame()
    X, Y, dates = make_windows(feats, target, lookback=60, horizons=(7, 30, 90))
    assert X.shape[1:] == (60, 5)
    assert Y.shape[1] == 3
    assert len(X) == len(Y) == len(dates)

def test_time_split_is_chronological():
    tr, va, te = time_split(100, train=0.7, val=0.15)
    assert (tr, va, te) == (slice(0, 70), slice(70, 85), slice(85, 100))

def test_model_forward_shape():
    out = LSTMCNN(n_features=5, n_horizons=3)(torch.randn(8, 60, 5))
    assert out.shape == (8, 3)

def test_model_overfits_tiny_batch():
    torch.manual_seed(0)
    model = LSTMCNN(n_features=4, n_horizons=2, dropout=0.0)
    x, y = torch.randn(16, 20, 4), torch.randn(16, 2)
    opt = torch.optim.Adam(model.parameters(), lr=1e-2)
    loss_fn = torch.nn.MSELoss()
    first = loss_fn(model(x), y).item()
    for _ in range(50):
        opt.zero_grad()
        loss = loss_fn(model(x), y)
        loss.backward()
        opt.step()
    assert loss.item() < first
