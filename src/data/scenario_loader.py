from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from ..config import DEMO_DATA_DIR, FEATURES, SEQ_LEN

class ScenarioLoader:
    """
    Manages loading, inspection, and temporal sliding-window playback of
    network state scenarios for the interactive SOC dashboard.
    """
    def __init__(self, demo_dir: Optional[Path] = None):
        self.demo_dir = Path(demo_dir) if demo_dir else DEMO_DATA_DIR
        self.scenarios: Dict[str, Path] = {}
        self.refresh_scenarios()

    def refresh_scenarios(self) -> Dict[str, Path]:
        """Discovers all scenario CSV files in the demo directory."""
        if not self.demo_dir.exists():
            self.demo_dir.mkdir(parents=True, exist_ok=True)

        self.scenarios = {
            p.stem.replace('_', ' ').title(): p
            for p in sorted(self.demo_dir.glob('*.csv'))
        }
        return self.scenarios

    def get_scenario_names(self) -> List[str]:
        return list(self.scenarios.keys())

    def load_scenario(self, name_or_path: str) -> pd.DataFrame:
        """Loads a scenario by friendly name or path."""
        if name_or_path in self.scenarios:
            path = self.scenarios[name_or_path]
        else:
            path = Path(name_or_path)

        if not path.exists():
            raise FileNotFoundError(f"Scenario file not found: {path}")

        df = pd.read_csv(path)
        if 'window' in df.columns:
            df['window'] = pd.to_datetime(df['window'])
        return df

    def get_sliding_window(
        self,
        df: pd.DataFrame,
        step_idx: int,
        seq_len: int = SEQ_LEN
    ) -> Tuple[np.ndarray, pd.Series, Optional[Dict[str, Any]]]:
        """
        Extracts a sequence of length seq_len up to step_idx.
        Returns:
            - history_matrix: np.ndarray of shape (seq_len, len(FEATURES))
            - current_state_row: pd.Series of the latest observed window
            - future_ground_truth: Dict with actual future values if available
        """
        if step_idx < seq_len:
            raise ValueError(f"step_idx ({step_idx}) must be >= seq_len ({seq_len})")
        if step_idx > len(df):
            raise ValueError(f"step_idx ({step_idx}) exceeds scenario length ({len(df)})")

        history_df = df.iloc[step_idx - seq_len:step_idx]
        history_features = history_df[FEATURES].to_numpy(dtype=np.float32)
        current_row = df.iloc[step_idx - 1]

        # Extract future ground truth if within bounds
        gt_data = None
        if step_idx < len(df):
            gt_next = df.iloc[step_idx]
            gt_data = {
                'next_risk': int(gt_next.get('attack_risk', 0)),
                'next_stage': str(gt_next.get('mitre_stage', 'Unknown')),
                'next_attack_fraction': float(gt_next.get('attack_fraction', 0.0))
            }

        return history_features, current_row, gt_data
