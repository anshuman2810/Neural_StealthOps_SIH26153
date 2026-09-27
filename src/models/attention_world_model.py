import torch
import torch.nn as nn
from typing import Tuple

class AttentionWorldModel(nn.Module):
    """
    Multi-task Attention-LSTM World Model for Cyber Attack Forecasting.
    
    Observes a temporal sequence of network states and simultaneously produces:
    1. Future network state vector (state transition dynamics)
    2. Direct threat risk logits at +10s, +30s, and +60s horizons
    3. Direct attack intensity (% malicious flows) at +10s, +30s, and +60s
    4. MITRE ATT&CK stage classification logits
    5. Temporal self-attention weights over historical windows
    """
    def __init__(
        self,
        n_features: int = 21,
        n_stages: int = 7,
        hidden_dim: int = 64,
        n_horizons: int = 3,
        dropout: float = 0.2
    ):
        super().__init__()
        self.n_features = n_features
        self.n_stages = n_stages
        self.hidden_dim = hidden_dim
        self.n_horizons = n_horizons

        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=dropout
        )
        self.score = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.Tanh(),
            nn.Linear(32, 1)
        )
        self.shared = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        self.state_head = nn.Linear(64, n_features)
        self.risk_head = nn.Linear(64, n_horizons)
        self.intensity_head = nn.Linear(64, n_horizons)
        self.stage_head = nn.Linear(64, n_stages)

    def forward(
        self,
        x: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass.
        Args:
            x: Input tensor of shape (batch_size, seq_len, n_features)
        Returns:
            state_pred: (batch_size, n_features)
            risk_logits: (batch_size, n_horizons)
            intensity_pred: (batch_size, n_horizons)
            stage_logits: (batch_size, n_stages)
            attention_weights: (batch_size, seq_len)
        """
        out, _ = self.lstm(x)  # (B, T, H)
        # Attention scores across temporal sequence
        weights = torch.softmax(self.score(out).squeeze(-1), dim=1)  # (B, T)
        # Attention-weighted context vector
        context = (out * weights.unsqueeze(-1)).sum(dim=1)  # (B, H)
        z = self.shared(context)  # (B, 64)

        state_pred = self.state_head(z)
        risk_logits = self.risk_head(z)
        intensity_pred = self.intensity_head(z)
        stage_logits = self.stage_head(z)

        return state_pred, risk_logits, intensity_pred, stage_logits, weights
