import numpy as np
import torch
from turballoc.forecast.model import LSTMCNN
from turballoc.forecast.train import get_device
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def load_model(chckp_path, device = None):
    device = device or get_device()
    ckpt = torch.load(chckp_path, map_location=device)
    model = LSTMCNN(n_features = ckpt["n_features"], n_horizons = ckpt["n_horizons"])
    model.load_state_dict(ckpt["model_state"])
    model.to(device).eval()
    return model, ckpt

def forecast(model, features, lookback = 60, device = None, ckpt = None):
    "Predict the latest forecast from the recent window, inverting the target transform."
    device = device or get_device()
    window = features.to_numpy(dtype="float32")[-lookback:]
    x = torch.as_tensor(window, dtype = torch.float32).unsqueeze(0).to(device)
    model.eval()
    with torch.no_grad():
        pred = model(x).cpu().numpy().ravel()
    if ckpt is not None:
        pred = pred * ckpt.get("target_std", 1.0) + ckpt.get("target_mean", 0.0)
        if ckpt.get("target_transform") == "log1p":
            pred = np.expm1(pred)
    return pred
    
