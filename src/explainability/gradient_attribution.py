from typing import List, Optional
import numpy as np
import pandas as pd
import torch

from ..config import FEATURES

class GradientAttributionExplainer:
    """
    Computes local feature importance using Gradient x Input attribution.
    Identifies which telemetry signals (TCP flags, volume, timing, entropy)
    are driving the threat risk forecast.
    """
    def __init__(self, predictor, features: Optional[List[str]] = None):
        self.predictor = predictor
        self.features = features if features else FEATURES

    def explain(
        self,
        raw_sequence: np.ndarray,
        horizon_idx: int = 1,
        top_k: int = 10
    ) -> pd.DataFrame:
        """
        Calculates Gradient x Input attribution for a given input sequence.
        
        Args:
            raw_sequence: Shape (seq_len, n_features)
            horizon_idx: Index of risk horizon (0: +10s, 1: +30s, 2: +60s)
            top_k: Number of top features to return
        Returns:
            pd.DataFrame containing feature names and attribution scores
        """
        model = self.predictor.model
        device = self.predictor.device

        if raw_sequence.ndim == 2:
            raw_sequence = raw_sequence[np.newaxis, :, :]

        scaled_sequence = self.predictor.scale_features(raw_sequence)
        sample = torch.tensor(scaled_sequence, dtype=torch.float32, device=device, requires_grad=True)

        model.eval()
        model.zero_grad(set_to_none=True)

        # cuDNN prohibits an LSTM backward pass in eval mode; temporarily disable cuDNN for attribution
        with torch.backends.cudnn.flags(enabled=False):
            _, risk_logits, _, _, _ = model(sample)
            target_risk = risk_logits[0, horizon_idx]
            target_risk.backward()

        if sample.grad is None:
            # Fallback if gradient is zero or not computed
            scores = np.zeros(len(self.features), dtype=np.float32)
        else:
            grad = sample.grad.detach().cpu().numpy()
            inp = sample.detach().cpu().numpy()
            # Gradient x Input magnitude averaged across batch and time dimensions
            scores = np.abs(grad * inp).mean(axis=(0, 1))

        df = pd.DataFrame({
            'feature': self.features,
            'importance': scores
        }).sort_values('importance', ascending=False).reset_index(drop=True)

        total_imp = df['importance'].sum()
        if total_imp > 0:
            df['relative_pct'] = (df['importance'] / total_imp) * 100.0
        else:
            df['relative_pct'] = 0.0

        return df.head(top_k)
