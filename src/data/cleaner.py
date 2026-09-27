from pathlib import Path
import re
import numpy as np
import pandas as pd
from typing import Tuple

from ..config import RAW_COLUMNS

def capture_date(path: Path) -> pd.Timestamp:
    """Extract and normalize the capture date from a CIC-IDS2018 CSV filename."""
    m = re.search(r'(\d{2}-\d{2}-\d{4})', path.name)
    if not m:
        raise ValueError(f"No capture date pattern found in {path.name}")
    return pd.to_datetime(m.group(1), format='%d-%m-%Y').normalize()

def clean_chunk(chunk: pd.DataFrame, expected_date: pd.Timestamp) -> Tuple[pd.DataFrame, int]:
    """
    Cleans a single chunk of CIC-IDS2018 flow records:
    - Strips whitespace from column names and string labels
    - Coerces timestamp with format '%d/%m/%Y %H:%M:%S'
    - Coerces numeric fields and replaces infinities with NaN
    - Discards corrupted rows: out-of-bounds duration, wrong date, or shifted header lines
    """
    chunk.columns = chunk.columns.str.strip()
    if 'Timestamp' not in chunk.columns or 'Label' not in chunk.columns:
        return pd.DataFrame(), len(chunk)

    chunk['Timestamp'] = pd.to_datetime(chunk['Timestamp'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    chunk['Label'] = chunk['Label'].astype(str).str.strip()

    numeric_cols = [c for c in RAW_COLUMNS if c not in ('Timestamp', 'Label') and c in chunk.columns]
    chunk[numeric_cols] = chunk[numeric_cols].apply(pd.to_numeric, errors='coerce').replace([np.inf, -np.inf], np.nan)

    valid_mask = (
        chunk['Timestamp'].notna() &
        chunk['Timestamp'].dt.normalize().eq(expected_date) &
        chunk['Flow Duration'].between(0, 86_400_000_000) &
        ~chunk['Label'].str.lower().eq('label')
    )

    cleaned = chunk.loc[valid_mask].copy()
    invalid_count = int((~valid_mask).sum())
    return cleaned, invalid_count
