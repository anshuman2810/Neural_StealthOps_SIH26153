from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from typing import Optional, List

from ..config import (
    RAW_COLUMNS, MEAN_SOURCE, SKEWED, WINDOW_SECONDS, CHUNK_SIZE,
    mitre_stage_from_label
)
from .cleaner import clean_chunk, capture_date

def build_states_for_file(
    path: Path,
    session_id: int = 0,
    max_chunks: Optional[int] = None,
    chunk_size: int = CHUNK_SIZE
) -> pd.DataFrame:
    """
    Builds chronological 10-second network states from a CIC-IDS2018 CSV file without
    loading the entire file into memory at once.
    """
    expected_date = capture_date(path)
    partials: List[pd.DataFrame] = []
    port_counts = defaultdict(Counter)
    label_counts = defaultdict(Counter)
    invalid_total = 0
    kept_total = 0

    chunk_idx = 0
    for chunk in pd.read_csv(
        path,
        usecols=lambda c: c.strip() in RAW_COLUMNS,
        chunksize=chunk_size,
        low_memory=False
    ):
        cleaned, bad_cnt = clean_chunk(chunk, expected_date)
        invalid_total += bad_cnt
        kept_total += len(cleaned)

        if not cleaned.empty:
            cleaned[MEAN_SOURCE] = cleaned[MEAN_SOURCE].fillna(0)
            cleaned['window'] = cleaned['Timestamp'].dt.floor(f'{WINDOW_SECONDS}s')
            cleaned['is_attack'] = ~cleaned['Label'].str.lower().eq('benign')
            cleaned['packet_total'] = cleaned['Tot Fwd Pkts'] + cleaned['Tot Bwd Pkts']
            cleaned['byte_total'] = cleaned['TotLen Fwd Pkts'] + cleaned['TotLen Bwd Pkts']

            sums = {f'{c}_sum': (c, 'sum') for c in MEAN_SOURCE}
            summary = cleaned.groupby('window', sort=False).agg(
                flow_count=('Label', 'size'),
                attack_flow_count=('is_attack', 'sum'),
                total_packets=('packet_total', 'sum'),
                total_bytes=('byte_total', 'sum'),
                protocol_diversity=('Protocol', 'nunique'),
                **sums
            )
            partials.append(summary)

            for (w, port), n in cleaned.groupby(['window', 'Dst Port']).size().items():
                port_counts[w][port] += int(n)
            for (w, label), n in cleaned.groupby(['window', 'Label']).size().items():
                label_counts[w][label] += int(n)

        chunk_idx += 1
        if max_chunks is not None and chunk_idx >= max_chunks:
            break

    if not partials:
        return pd.DataFrame()

    merged = pd.concat(partials).groupby(level=0).sum().sort_index()
    states = []

    for window, row in merged.iterrows():
        ports = port_counts[window]
        p = np.asarray(list(ports.values()), dtype=float)
        p = p / max(p.sum(), 1.0)
        port_entropy = float(-(p * np.log2(p + 1e-12)).sum())

        labels = label_counts[window]
        malicious = {lab: n for lab, n in labels.items() if lab.lower() != 'benign'}
        dominant = 'Benign' if not malicious else max(malicious, key=malicious.get)

        record = {
            'session_id': session_id,
            'window': window,
            'flow_count': row.flow_count,
            'total_packets': row.total_packets,
            'total_bytes': row.total_bytes,
            'attack_flow_count': row.attack_flow_count,
            'attack_fraction': row.attack_flow_count / max(row.flow_count, 1.0),
            'unique_dst_ports': len(ports),
            'port_entropy': port_entropy,
            'protocol_diversity': row.protocol_diversity,
            'raw_label': dominant,
            'mitre_stage': mitre_stage_from_label(dominant)
        }

        for c in MEAN_SOURCE:
            record[f'mean_{c}'] = row[f'{c}_sum'] / max(row.flow_count, 1.0)

        states.append(record)

    df_states = pd.DataFrame(states)
    if df_states.empty:
        return df_states

    # Calculate engineered log features
    for c in SKEWED:
        df_states[f'log_{c}'] = np.log1p(df_states[c].clip(lower=0))

    # Binary attack risk ground truth
    df_states['attack_risk'] = (
        (df_states['attack_fraction'] >= 0.05) | (df_states['attack_flow_count'] >= 5)
    ).astype(np.int64)

    return df_states

def aggregate_states_from_chunks(chunks_list: List[pd.DataFrame], session_id: int = 0) -> pd.DataFrame:
    """Helper to aggregate in-memory chunks into states."""
    if not chunks_list:
        return pd.DataFrame()
    return pd.concat(chunks_list, ignore_index=True)
