import sys
from pathlib import Path
import time
import streamlit as st
import pandas as pd
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import SEQ_LEN, WINDOW_SECONDS, ARTIFACTS_DIR
from src.data.scenario_loader import ScenarioLoader
from src.models.predictor import NetworkWorldModelPredictor
from src.explainability.gradient_attribution import GradientAttributionExplainer
from src.explainability.attention_explainer import AttentionExplainer
from src.simulation.rollout import AutoregressiveRolloutSimulator

from dashboard.components import (
    render_header,
    render_metrics,
    render_mitre_matrix,
    render_telemetry_charts,
    render_rollout_view,
    render_xai_panel,
    render_alert_feed
)

# Configure Streamlit page
st.set_page_config(
    page_title="Predictive World Model — SOC Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom dark-theme styling
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0b1120;
            color: #f1f5f9;
        }
        section[data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
        }
        .stMetric {
            background-color: #1e293b;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #334155;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_resource
def load_ai_engine():
    """Initializes and caches the trained PyTorch inference and explanation engines."""
    predictor = NetworkWorldModelPredictor()
    grad_explainer = GradientAttributionExplainer(predictor)
    attn_explainer = AttentionExplainer(seq_len=SEQ_LEN, window_seconds=WINDOW_SECONDS)
    rollout_sim = AutoregressiveRolloutSimulator(predictor)
    return predictor, grad_explainer, attn_explainer, rollout_sim

def main():
    loader = ScenarioLoader()
    scenario_names = loader.get_scenario_names()

    # Sidebar Controls
    with st.sidebar:
        st.markdown("## ⚙️ SOC Replay Controller")

        if not scenario_names:
            st.error("No scenario files found in `demo_data/`! Run `python scripts/precompute_scenarios.py` first.")
            st.stop()

        selected_scenario_name = st.selectbox(
            "Select Attack Scenario",
            scenario_names,
            index=0
        )

        df_scenario = loader.load_scenario(selected_scenario_name)
        total_steps = len(df_scenario)

        st.markdown("---")
        st.markdown("### ⏯️ Playback Mode")

        # Initialize session state for playback step
        if 'step_idx' not in st.session_state:
            st.session_state.step_idx = SEQ_LEN
        if 'is_playing' not in st.session_state:
            st.session_state.is_playing = False
        if 'current_scenario' not in st.session_state or st.session_state.current_scenario != selected_scenario_name:
            st.session_state.current_scenario = selected_scenario_name
            st.session_state.step_idx = SEQ_LEN

        mode = st.radio("Simulation Control", ["Manual Step Slider", "Live Stream Replay"], index=0)

        if mode == "Manual Step Slider":
            st.session_state.is_playing = False
            step_idx = st.slider(
                "Window Index (10s intervals)",
                min_value=SEQ_LEN,
                max_value=total_steps,
                value=st.session_state.step_idx,
                step=1
            )
            st.session_state.step_idx = step_idx
        else:
            col_play, col_pause, col_reset = st.columns(3)
            with col_play:
                if st.button("▶️ Play", use_container_width=True):
                    st.session_state.is_playing = True
            with col_pause:
                if st.button("⏸️ Pause", use_container_width=True):
                    st.session_state.is_playing = False
            with col_reset:
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.step_idx = SEQ_LEN
                    st.session_state.is_playing = False

            speed = st.select_slider(
                "Replay Speed (delay per window)",
                options=[0.5, 1.0, 1.5, 2.0],
                value=1.0,
                format_func=lambda x: f"{x}s / window"
            )

        st.markdown("---")
        st.markdown("### 🧠 AI Engine Architecture")
        st.caption(f"**Model:** PyTorch AttentionWorldModel (Multi-Task)")
        st.caption(f"**Context Window:** {SEQ_LEN} states ({SEQ_LEN * WINDOW_SECONDS}s history)")
        st.caption(f"**Direct Horizons:** +10s, +30s, +60s")
        st.caption(f"**Explainability:** Self-Attention + Grad × Input")

    # Load Model Engine
    try:
        predictor, grad_explainer, attn_explainer, rollout_sim = load_ai_engine()
    except Exception as e:
        st.error(f"Error loading AI model: {e}")
        st.info("Ensure `artifacts_v2/attention_world_model.pt` exists and dependencies are installed.")
        st.stop()

    # Extract current window sequence
    curr_step = st.session_state.step_idx
    history_features, current_row, gt_future = loader.get_sliding_window(
        df_scenario, curr_step, seq_len=SEQ_LEN
    )

    history_df = df_scenario.iloc[curr_step - SEQ_LEN:curr_step]
    current_time_str = str(current_row.get('window', f'Step {curr_step}'))

    # Run AI Inference
    prediction = predictor.predict(history_features)
    attribution_df = grad_explainer.explain(history_features, horizon_idx=1, top_k=8)
    attention_df = attn_explainer.explain(prediction['attention_weights'])
    rollout_df = rollout_sim.simulate(history_features, k_steps=6)

    # 1. Executive Banner
    render_header(
        scenario_name=selected_scenario_name,
        current_window=current_time_str,
        threat_level=prediction['threat_level']
    )

    # 2. Executive KPI Cards
    render_metrics(prediction=prediction, current_state=current_row.to_dict())

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. MITRE ATT&CK Kill-Chain Matrix
    render_mitre_matrix(
        predicted_stage=prediction['predicted_stage'],
        stage_probs=prediction['stage_probabilities']
    )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 4. 60-Second Rollout Trajectory Simulation
    render_rollout_view(rollout_df=rollout_df)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 5. Real-Time Telemetry Stream
    render_telemetry_charts(history_df=history_df)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 6. Explainable AI Diagnostics (XAI)
    render_xai_panel(attention_df=attention_df, attribution_df=attribution_df)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 7. Incident Feed & Automated Response Playbooks
    render_alert_feed(prediction=prediction, current_state=current_row.to_dict())

    # Handle Live Stream Playback progression
    if st.session_state.is_playing:
        if st.session_state.step_idx < total_steps:
            time.sleep(speed)
            st.session_state.step_idx += 1
            st.rerun()
        else:
            st.session_state.is_playing = False
            st.warning("Reached end of scenario sequence.")

if __name__ == "__main__":
    main()
