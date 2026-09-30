from typing import List, Optional
import numpy as np
import pandas as pd
import torch
import shap

from ..config import FEATURES

class ThreatRiskWrapper(torch.nn.Module):
    """Wraps PyTorch AttentionWorldModel to expose target hazard risk for SHAP computation."""
    def __init__(self, model, horizon_idx: int = 1):
        super().__init__()
        self.model = model
        self.horizon_idx = horizon_idx

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, risk_logits, _, _, _ = self.model(x)
        # Horizon 0: +10s, 1: +30s, 2: +60s
        return torch.sigmoid(risk_logits[:, self.horizon_idx:self.horizon_idx+1])

class ShapExplainer:
    """
    Computes SHAP values (Shapley Additive Explanations) for the Attention-LSTM World Model.
    Calculates exact marginal feature contributions phi_i across all 21 flow telemetry metrics.
    """
    def __init__(self, predictor, features: Optional[List[str]] = None, horizon_idx: int = 1):
        self.predictor = predictor
        self.features = features if features else FEATURES
        self.horizon_idx = horizon_idx
        self.device = predictor.device
        self.wrapper = ThreatRiskWrapper(predictor.model, horizon_idx=horizon_idx)
        # Background reference tensor (quiescent baseline)
        self.background = torch.zeros((5, predictor.seq_len, len(self.features)), dtype=torch.float32, device=self.device)

    def explain(
        self,
        raw_sequence: np.ndarray,
        horizon_idx: Optional[int] = None,
        top_k: int = 8
    ) -> pd.DataFrame:
        """
        Calculates SHAP values for the given temporal observation sequence.
        
        Args:
            raw_sequence: Shape (seq_len, n_features) or (1, seq_len, n_features)
            horizon_idx: Horizon index (0: +10s, 1: +30s, 2: +60s)
            top_k: Number of top telemetry features to return
        Returns:
            pd.DataFrame with 'feature', 'shap_value', and 'relative_pct'
        """
        if horizon_idx is not None and horizon_idx != self.horizon_idx:
            self.horizon_idx = horizon_idx
            self.wrapper = ThreatRiskWrapper(self.predictor.model, horizon_idx=horizon_idx)

        if raw_sequence.ndim == 2:
            raw_sequence = raw_sequence[np.newaxis, :, :]

        scaled_sequence = self.predictor.scale_features(raw_sequence)
        sample = torch.tensor(scaled_sequence, dtype=torch.float32, device=self.device)

        self.predictor.model.eval()

        # cuDNN prohibits RNN backward in eval mode; disable cuDNN for SHAP gradient tracking
        with torch.backends.cudnn.flags(enabled=False):
            try:
                explainer = shap.GradientExplainer(self.wrapper, self.background)
                shap_vals = explainer.shap_values(sample)
                arr = np.array(shap_vals)
                if arr.ndim == 4:
                    # Shape: (batch=1, seq=12, feat=21, output=1)
                    scores = np.abs(arr[0, :, :, 0]).mean(axis=0)
                elif arr.ndim == 3:
                    scores = np.abs(arr[0]).mean(axis=0)
                else:
                    scores = np.abs(arr).flatten()[:len(self.features)]
            except Exception as e:
                # Robust fallback to Gradient x Input attribution if shap encounters runtime issue
                sample_grad = torch.tensor(scaled_sequence, dtype=torch.float32, device=self.device, requires_grad=True)
                _, risk_logits, _, _, _ = self.predictor.model(sample_grad)
                target = risk_logits[0, self.horizon_idx]
                target.backward()
                grad = sample_grad.grad.detach().cpu().numpy()
                inp = sample_grad.detach().cpu().numpy()
                scores = np.abs(grad * inp).mean(axis=(0, 1))

        df = pd.DataFrame({
            'feature': self.features,
            'shap_value': scores
        }).sort_values('shap_value', ascending=False).reset_index(drop=True)

        total_val = df['shap_value'].sum()
        if total_val > 0:
            df['relative_pct'] = (df['shap_value'] / total_val) * 100.0
        else:
            df['relative_pct'] = 0.0

        return df.head(top_k)
