import torch
from torch import nn
from tqdm import tqdm
from torch.utils.data import DataLoader
from turballoc.config import settings
from turballoc.forecast.dataset import SeqData, make_windows, time_split
from turballoc.forecast.model import LSTMCNN
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train_model(features, target, lookback = 60, epochs = 30, batch = 64, lr =1e-3, ckpt_path = None):
    torch.manual_seed(settings.random_seed)
    X, Y, _ = make_windows(features, target, lookback=lookback)
    tr, va, _ = time_split(len(X))
    # Standardize the (log) target on the train split so the head learns the shape, not the
    # offset, and the optimizer isn't dragged around by the target's scale. Stats are saved
    # in the checkpoint and inverted at inference (predict.forecast).
    t_mean = float(Y[tr].mean())
    t_std = float(Y[tr].std()) or 1.0
    Yn = (Y - t_mean) / t_std
    device = get_device()
    model = LSTMCNN(n_features=X.shape[2], n_horizons=Y.shape[1]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr = lr)
    loss_fn = nn.MSELoss()
    train_dl = DataLoader(SeqData(X[tr], Yn[tr]), batch_size=batch, shuffle = True)
    val_ds = SeqData(X[va], Yn[va])

    for epoch in tqdm(range(1, epochs + 1)):
        model.train()
        total = 0.0
        for xb, yb in train_dl:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
            total += loss.item() * len(xb)
        train_loss = total / len(train_dl.dataset)
        val_loss = _evaluate(model, val_ds, loss_fn, device)
        logger.info("epoch %d | train_mse %.5f | val_mse %.5f", epoch, train_loss, val_loss)

    if ckpt_path:
        torch.save({"model_state": model.state_dict(),
                    "optimizer_state": opt.state_dict(),
                    "n_features": X.shape[2], "n_horizons": Y.shape[1], "lookback": lookback,
                    "target_mean": t_mean, "target_std": t_std, "target_transform": "log1p"},
                    ckpt_path)
        logger.info(f"Saved checkpoint to: {ckpt_path}")
    return model

def _evaluate(model, dataset, loss_fn, device):
    model.eval()
    with torch.no_grad():
        return loss_fn(model(dataset.X.to(device)), dataset.Y.to(device)).item() 
