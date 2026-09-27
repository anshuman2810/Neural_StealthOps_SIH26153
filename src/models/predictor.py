from pathlib import Path
from typing import Dict, Any, Optional, Union
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.preprocessing import StandardScaler

from ..config import (
    ARTIFACTS_DIR, FEATURES, STAGES, HORIZONS, SEQ_LEN
)
from .attention_world_model import AttentionWorldModel

class NetworkWorldModelPredictor:
    """
    Inference and forecasting controller.
    Loads the trained PyTorch AttentionWorldModel, handles scaling,
    and returns multi-horizon risk assessments, stage classifications,
    and attention weights.
    """
    def __init__(
        self,
        checkpoint_path: Optional[Union[str, Path]] = None,
        scaler_path: Optional[Union[str, Path]] = None,
        device: Optional[str] = None
    ):
        self.device = torch.device(
            device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        )
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else (ARTIFACTS_DIR / "attention_world_model.pt")
        self.scaler_path = Path(scaler_path) if scaler_path else (ARTIFACTS_DIR / "scaler.npz")

        self.features = FEATURES
        self.stages = STAGES
        self.horizons = HORIZONS
        self.seq_len = SEQ_LEN

        self.model: Optional[AttentionWorldModel] = None
        self.scaler: Optional[StandardScaler] = None

        self._load_model()
        self._load_scaler()

    def _load_model(self) -> None:
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Model checkpoint not found at: {self.checkpoint_path}")

        ckpt = torch.load(self.checkpoint_path, map_location=self.device)
        self.features = ckpt.get('features', self.features)
        self.stages = ckpt.get('stages', self.stages)
        self.seq_len = ckpt.get('sequence_length', self.seq_len)

        self.model = AttentionWorldModel(
            n_features=len(self.features),
            n_stages=len(self.stages),
            hidden_dim=64,
            n_horizons=len(self.horizons)
        ).to(self.device)

        state_dict = ckpt.get('state_dict', ckpt.get('model_state_dict', ckpt))
        self.model.load_state_dict(state_dict)
        self.model.eval()

    def _load_scaler(self) -> None:
        """Loads mean and scale parameters into a StandardScaler instance."""
        if self.scaler_path.exists():
            data = np.load(self.scaler_path)
            self.scaler = StandardScaler()
            self.scaler.mean_ = data['mean']
            self.scaler.scale_ = data['scale']
            self.scaler.var_ = data['scale'] ** 2
            self.scaler.n_features_in_ = len(data['mean'])
        else:
            self.scaler = None

    def fit_scaler(self, X_train: np.ndarray) -> None:
        """Utility to fit and cache scaler if not loaded from file."""
        self.scaler = StandardScaler().fit(X_train)
        if self.scaler_path.parent.exists():
            np.savez(self.scaler_path, mean=self.scaler.mean_, scale=self.scaler.scale_)

    def scale_features(self, X: np.ndarray) -> np.ndarray:
        if self.scaler is not None:
            # If 3D (batch, seq, feat)
            if X.ndim == 3:
                b, s, f = X.shape
                flat = X.reshape(-1, f)
                scaled = self.scaler.transform(flat)
                return scaled.reshape(b, s, f).astype(np.float32)
            # If 2D (seq, feat)
            return self.scaler.transform(X).astype(np.float32)
        return X.astype(np.float32)

    def inverse_scale_features(self, X_scaled: np.ndarray) -> np.ndarray:
        if self.scaler is not None:
            if X_scaled.ndim == 2:
                return self.scaler.inverse_transform(X_scaled)
            elif X_scaled.ndim == 1:
                return self.scaler.inverse_transform(X_scaled.reshape(1, -1))[0]
        return X_scaled

    def predict(self, raw_sequence: np.ndarray) -> Dict[str, Any]:
        """
        Executes multi-task inference for a single window sequence of length seq_len.
        
        Args:
            raw_sequence: np.ndarray of shape (seq_len, n_features) or (1, seq_len, n_features)
        Returns:
            Dictionary with forecasts, probabilities, threat status, and attention weights.
        """
        if self.model is None:
            raise RuntimeError("Model is not initialized.")

        if raw_sequence.ndim == 2:
            raw_sequence = raw_sequence[np.newaxis, :, :]

        scaled_sequence = self.scale_features(raw_sequence)
        x_tensor = torch.tensor(scaled_sequence, dtype=torch.float32, device=self.device)

        with torch.no_grad():
            state_pred, risk_logits, intensity_pred, stage_logits, weights = self.model(x_tensor)

            # Probabilities
            risk_probs = torch.sigmoid(risk_logits)[0].cpu().numpy()
            stage_probs = F.softmax(stage_logits, dim=-1)[0].cpu().numpy()
            intensity_values = intensity_pred[0].cpu().numpy()
            attention_w = weights[0].cpu().numpy()
            next_state_scaled = state_pred[0].cpu().numpy()

        next_state_unscaled = self.inverse_scale_features(next_state_scaled)
        pred_stage_idx = int(np.argmax(stage_probs))
        pred_stage_name = self.stages[pred_stage_idx]

        # Calculate composite threat level
        max_risk = float(np.max(risk_probs))
        if max_risk < 0.20:
            threat_level = "NORMAL"
        elif max_risk < 0.60:
            threat_level = "ELEVATED"
        elif max_risk < 0.85:
            threat_level = "HIGH"
        else:
            threat_level = "CRITICAL"

        return {
            "threat_level": threat_level,
            "max_risk": max_risk,
            "risk_10s": float(risk_probs[0]),
            "risk_30s": float(risk_probs[1]),
            "risk_60s": float(risk_probs[2]),
            "intensity_10s": float(np.clip(intensity_values[0], 0.0, 1.0)),
            "intensity_30s": float(np.clip(intensity_values[1], 0.0, 1.0)),
            "intensity_60s": float(np.clip(intensity_values[2], 0.0, 1.0)),
            "predicted_stage": pred_stage_name,
            "stage_confidence": float(stage_probs[pred_stage_idx]),
            "stage_probabilities": {stage: float(prob) for stage, prob in zip(self.stages, stage_probs)},
            "attention_weights": attention_w,
            "next_state_scaled": next_state_scaled,
            "next_state_unscaled": next_state_unscaled,
            "scaled_input": scaled_sequence[0]
        }
