from typing import Optional
import numpy as np
import pandas as pd

from ..config import WINDOW_SECONDS, SEQ_LEN

class AttentionExplainer:
    """
    Interprets temporal self-attention weights from the AttentionWorldModel.
    Shows which preceding 10-second windows triggered the early threat detection.
    """
    def __init__(self, seq_len: int = SEQ_LEN, window_seconds: int = WINDOW_SECONDS):
        self.seq_len = seq_len
        self.window_seconds = window_seconds

    def explain(self, attention_weights: np.ndarray) -> pd.DataFrame:
        """
        Formats raw attention weights into a clean, human-interpretable DataFrame.
        Args:
            attention_weights: 1D array of shape (seq_len,)
        """
        weights = np.asarray(attention_weights, dtype=np.float32).flatten()
        if len(weights) != self.seq_len:
            # Pad or truncate if needed
            if len(weights) < self.seq_len:
                weights = np.pad(weights, (self.seq_len - len(weights), 0))
            else:
                weights = weights[-self.seq_len:]

        # Create relative time offset labels
        # e.g., for seq_len=12, windows are -110s, -100s, ..., -10s, "Current (t=0s)"
        labels = []
        for i in range(self.seq_len):
            offset_seconds = (self.seq_len - 1 - i) * self.window_seconds
            if offset_seconds == 0:
                labels.append("t = 0s (Latest)")
            else:
                labels.append(f"t - {offset_seconds}s")

        df = pd.DataFrame({
            'window_index': list(range(self.seq_len)),
            'time_offset': labels,
            'attention_weight': weights,
            'percentage': (weights / max(weights.sum(), 1e-12)) * 100.0
        })

        return df
