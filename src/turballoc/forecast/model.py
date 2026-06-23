import torch
from torch import nn

class LSTMCNN(nn.Module):
    "Conv1d -> LSTM -> attention pooling -> linear head for multi-horizon forecasts"
    def __init__(self, n_features, n_horizons = 3, conv_channels = 32,
                 lstm_hidden = 64, kernel_size = 3,  dropout = 0.2):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(n_features, conv_channels, kernel_size, padding = kernel_size//2),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        self.lstm = nn.LSTM(conv_channels, lstm_hidden, batch_first=True)
        self.attn = nn.Linear(lstm_hidden, 1)
        self.head = nn.Sequential(
            nn.Linear(lstm_hidden, lstm_hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(lstm_hidden, n_horizons)
        )
    
    def forward(self, x):
        # x: (batch, lookback, features)
        h = self.conv(x.transpose(1, 2))       #(batch, channels, lookback)
        out, _ = self.lstm(h.transpose(1, 2))  #(batch, lookback, hidden)
        weights = torch.softmax(self.attn(out).squeeze(-1), dim = 1)  #(batch, lookback)
        context = (out * weights.unsqueeze(-1)).sum(dim = 1)      #(batch, hidden)
        return self.head(context)      #(batch, n_horizons)
