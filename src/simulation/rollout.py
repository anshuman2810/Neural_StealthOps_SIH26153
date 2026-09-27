from typing import Dict, Any, List
import numpy as np
import pandas as pd
import torch

from ..config import WINDOW_SECONDS, STAGES

class AutoregressiveRolloutSimulator:
    """
    Simulates future multi-step network state trajectories.
    Recursively predicts the next state vector, appends it to the rolling
    history, and forecasts the evolving risk and MITRE attack stage over 60+ seconds.
    """
    def __init__(self, predictor):
        self.predictor = predictor
        self.window_seconds = WINDOW_SECONDS
        self.stages = STAGES

    def simulate(self, raw_history: np.ndarray, k_steps: int = 6) -> pd.DataFrame:
        """
        Runs a k-step forward autoregressive rollout simulation.
        
        Args:
            raw_history: Input array of shape (seq_len, n_features)
            k_steps: Number of forward windows (6 steps = 60 seconds)
        Returns:
            pd.DataFrame containing simulated future timeline
        """
        model = self.predictor.model
        device = self.predictor.device

        # Scale the initial history
        if raw_history.ndim == 2:
            raw_history = raw_history[np.newaxis, :, :]
        scaled_hist = self.predictor.scale_features(raw_history)[0]  # (seq_len, n_features)

        rows: List[Dict[str, Any]] = []
        hist = scaled_hist.copy().astype(np.float32)

        model.eval()
        with torch.no_grad():
            for step in range(1, k_steps + 1):
                input_tensor = torch.tensor(hist[None], dtype=torch.float32, device=device)
                state_pred, risk_logits, intensity_pred, stage_logits, _ = model(input_tensor)

                step_risk = float(torch.sigmoid(risk_logits[0, 0]).cpu().numpy())
                step_stage_idx = int(stage_logits.argmax(dim=-1)[0].cpu().numpy())
                step_stage = self.stages[step_stage_idx]
                step_intensity = float(np.clip(intensity_pred[0, 0].cpu().numpy(), 0.0, 1.0))
                next_scaled_state = state_pred[0].cpu().numpy()

                # Unscale the predicted state to view human-readable network metrics
                unscaled_state = self.predictor.inverse_scale_features(next_scaled_state)

                row_dict = {
                    'step': step,
                    'seconds_ahead': step * self.window_seconds,
                    'predicted_risk': step_risk,
                    'risk_pct': step_risk * 100.0,
                    'predicted_stage': step_stage,
                    'predicted_intensity': step_intensity
                }

                # Add sample telemetry projections if available
                feature_names = self.predictor.features
                if 'mean_Flow Pkts/s' in feature_names:
                    row_dict['proj_flow_pkts_s'] = float(unscaled_state[feature_names.index('mean_Flow Pkts/s')])
                if 'port_entropy' in feature_names:
                    row_dict['proj_port_entropy'] = float(unscaled_state[feature_names.index('port_entropy')])
                if 'mean_RST Flag Cnt' in feature_names:
                    row_dict['proj_rst_flags'] = float(unscaled_state[feature_names.index('mean_RST Flag Cnt')])

                rows.append(row_dict)

                # Recursive state update: roll history buffer and append newly simulated state
                hist = np.vstack([hist[1:], next_scaled_state])

        return pd.DataFrame(rows)
