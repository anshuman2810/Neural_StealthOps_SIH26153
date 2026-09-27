import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.config import (
    DATA_DIR, DEMO_DATA_DIR, ARTIFACTS_DIR, FEATURES, RAW_COLUMNS
)
from src.data.state_builder import build_states_for_file

def generate_scenario(
    csv_name: str,
    scenario_filename: str,
    max_chunks: int = 10,
    slice_length: int = 120,
    prioritize_attack: bool = True
) -> pd.DataFrame:
    """
    Extracts a representative chronological slice of network states from a dataset CSV.
    """
    csv_path = DATA_DIR / csv_name
    if not csv_path.exists():
        print(f"Warning: {csv_name} not found in {DATA_DIR}. Skipping.")
        return pd.DataFrame()

    print(f"Processing {csv_name} (max {max_chunks} chunks)...")
    states = build_states_for_file(csv_path, session_id=0, max_chunks=max_chunks)

    if states.empty:
        print(f"No valid states generated for {csv_name}.")
        return pd.DataFrame()

    print(f"Generated {len(states)} states. Attack states: {(states['attack_risk'] == 1).sum()}")

    if prioritize_attack and (states['attack_risk'] == 1).any():
        # Find the first attack window and take a window buffer before and after it
        first_atk_idx = states[states['attack_risk'] == 1].index[0]
        # Include at least 25 windows of normal traffic before the attack
        start_idx = max(0, first_atk_idx - 25)
        end_idx = min(len(states), start_idx + slice_length)
        scenario_df = states.iloc[start_idx:end_idx].copy().reset_index(drop=True)
    else:
        # Take the initial slice
        scenario_df = states.iloc[:slice_length].copy().reset_index(drop=True)

    out_path = DEMO_DATA_DIR / scenario_filename
    scenario_df.to_csv(out_path, index=False)
    print(f"Saved demo scenario ({len(scenario_df)} windows) to {out_path}")
    return scenario_df

def main():
    DEMO_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    print("==========================================================")
    print("Building Lightweight Demo Scenarios for SOC Dashboard")
    print("==========================================================")

    all_states = []

    # Scenario 1: Botnet C2 Surge (Friday-02-03-2018)
    df_bot = generate_scenario(
        csv_name="Friday-02-03-2018_TrafficForML_CICFlowMeter.csv",
        scenario_filename="1_botnet_c2_attack.csv",
        max_chunks=8,
        slice_length=100,
        prioritize_attack=True
    )
    if not df_bot.empty:
        all_states.append(df_bot)

    # Scenario 2: Network Infiltration / Lateral Movement (Thursday-01-03-2018)
    df_infilt = generate_scenario(
        csv_name="Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv",
        scenario_filename="2_infiltration_lateral_movement.csv",
        max_chunks=6,
        slice_length=100,
        prioritize_attack=True
    )
    if not df_infilt.empty:
        all_states.append(df_infilt)

    # Scenario 3: SSH/FTP Credential Brute Force (Wednesday-14-02-2018)
    df_ssh = generate_scenario(
        csv_name="Wednesday-14-02-2018_TrafficForML_CICFlowMeter.csv",
        scenario_filename="3_credential_brute_force.csv",
        max_chunks=6,
        slice_length=100,
        prioritize_attack=True
    )
    if not df_ssh.empty:
        all_states.append(df_ssh)

    # Scenario 4: DDoS Impact Storm (Wednesday-21-02-2018)
    df_ddos = generate_scenario(
        csv_name="Wednesday-21-02-2018_TrafficForML_CICFlowMeter.csv",
        scenario_filename="4_ddos_high_impact.csv",
        max_chunks=6,
        slice_length=100,
        prioritize_attack=True
    )
    if not df_ddos.empty:
        all_states.append(df_ddos)

    # Scenario 5: Normal Network Baseline (Benign only)
    if not df_bot.empty:
        benign_slice = df_bot[df_bot['attack_risk'] == 0].head(80).copy().reset_index(drop=True)
        if len(benign_slice) >= 30:
            out_path = DEMO_DATA_DIR / "5_normal_network_baseline.csv"
            benign_slice.to_csv(out_path, index=False)
            print(f"Saved normal baseline scenario to {out_path}")

    # Build and cache scaler for artifacts_v2
    scaler_out = ARTIFACTS_DIR / "scaler.npz"
    if all_states:
        combined = pd.concat(all_states, ignore_index=True)
        scaler = StandardScaler().fit(combined[FEATURES])
        np.savez(scaler_out, mean=scaler.mean_, scale=scaler.scale_)
        print(f"\nSuccessfully fitted and saved standard scaler to {scaler_out}")
    else:
        print("\nWarning: No states loaded, could not fit scaler.")

    print("\nPrecomputation complete! Demo scenarios ready in demo_data/")

if __name__ == "__main__":
    main()
