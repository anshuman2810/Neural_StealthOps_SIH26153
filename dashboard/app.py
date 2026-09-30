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
from src.explainability.shap_explainer import ShapExplainer
from src.explainability.attention_explainer import AttentionExplainer
from src.simulation.rollout import AutoregressiveRolloutSimulator
from src.simulation.port_engine import PortTelemetryEngine

from dashboard.components import (
    render_header,
    render_metrics,
    render_mitre_matrix,
    render_port_analysis,
    render_telemetry_charts,
    render_rollout_view,
    render_xai_panel,
    render_alert_feed
)

# Configure Streamlit page with clean title and no emojis
st.set_page_config(
    page_title="Predictive World Model — SOC Console",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom high-contrast light enterprise styling
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f1f5f9;
            color: #0f172a;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1.5px solid #cbd5e1;
        }
        .stMetric {
            background-color: #ffffff;
            padding: 12px;
            border-radius: 8px;
            border: 1.5px solid #cbd5e1;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 14px;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff;
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 8px;
            padding: 14px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
            border: 1.5px solid #cbd5e1;
            background-color: #ffffff;
            color: #0f172a;
            transition: all 0.15s ease-in-out;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        }
        .stButton>button:hover {
            border-color: #2563eb;
            color: #2563eb;
            background-color: #f8fafc;
        }
        h2, h3, h4 {
            color: #0f172a !important;
            font-weight: 700 !important;
            letter-spacing: -0.3px;
        }
        .stCaption {
            color: #475569 !important;
            font-size: 0.85rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_resource
def load_ai_engine():
    """Initializes and caches the trained PyTorch inference, explanation, and port engines."""
    predictor = NetworkWorldModelPredictor()
    shap_explainer = ShapExplainer(predictor)
    attn_explainer = AttentionExplainer(seq_len=SEQ_LEN, window_seconds=WINDOW_SECONDS)
    rollout_sim = AutoregressiveRolloutSimulator(predictor)
    port_engine = PortTelemetryEngine()
    return predictor, shap_explainer, attn_explainer, rollout_sim, port_engine

@st.cache_data(show_spinner=False)
def get_cached_scenario(scenario_name: str) -> pd.DataFrame:
    """Loads and caches scenario telemetry in RAM to eliminate repeated disk I/O across sessions."""
    loader = ScenarioLoader()
    return loader.load_scenario(scenario_name)

@st.cache_data(show_spinner=False, max_entries=2000)
def compute_step_diagnostics(scenario_name: str, step_idx: int):
    """
    Computes and caches AI inference, SHAP feature attributions, self-attention,
    60-second autoregressive rollout, and port transitions for a given scenario step.
    Caches results across all concurrent user sessions for sub-millisecond instant response.
    """
    loader = ScenarioLoader()
    df_scenario = get_cached_scenario(scenario_name)
    predictor, shap_explainer, attn_explainer, rollout_sim, port_engine = load_ai_engine()

    history_features, current_row, gt_future = loader.get_sliding_window(
        df_scenario, step_idx, seq_len=SEQ_LEN
    )
    current_time_str = str(current_row.get('window', f'Step {step_idx}'))

    # Run AI Inference
    prediction = predictor.predict(history_features)
    attribution_df = shap_explainer.explain(history_features, horizon_idx=1, top_k=8)
    attention_df = attn_explainer.explain(prediction['attention_weights'])
    rollout_df = rollout_sim.simulate(history_features, k_steps=6)
    port_transition_data = port_engine.get_port_state_transitions(current_row.to_dict(), prediction, scenario_name)

    return {
        "prediction": prediction,
        "attribution_df": attribution_df,
        "attention_df": attention_df,
        "rollout_df": rollout_df,
        "port_transition_data": port_transition_data,
        "current_row_dict": current_row.to_dict(),
        "current_time_str": current_time_str
    }

def main():
    loader = ScenarioLoader()
    scenario_names = loader.get_scenario_names()

    # Sidebar Controls
    with st.sidebar:
        st.markdown("## SOC Replay Controller")

        if not scenario_names:
            st.error("No scenario files found in demo_data! Run python scripts/precompute_scenarios.py first.")
            st.stop()

        selected_scenario_name = st.selectbox(
            "Select Attack Scenario",
            scenario_names,
            index=0
        )

        df_scenario = get_cached_scenario(selected_scenario_name)
        total_steps = len(df_scenario)

        st.markdown("---")
        st.markdown("### Playback Mode")

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
                if st.button("Play", use_container_width=True):
                    st.session_state.is_playing = True
            with col_pause:
                if st.button("Pause", use_container_width=True):
                    st.session_state.is_playing = False
            with col_reset:
                if st.button("Reset", use_container_width=True):
                    st.session_state.step_idx = SEQ_LEN
                    st.session_state.is_playing = False

            speed = st.select_slider(
                "Replay Speed (delay per window)",
                options=[0.5, 1.0, 1.5, 2.0],
                value=1.0,
                format_func=lambda x: f"{x}s / window"
            )

        st.markdown("---")
        st.markdown("### AI Engine Architecture")
        st.caption(f"**Model:** PyTorch AttentionWorldModel (Multi-Task)")
        st.caption(f"**Context Window:** {SEQ_LEN} states ({SEQ_LEN * WINDOW_SECONDS}s history)")
        st.caption(f"**Direct Horizons:** +10s, +30s, +60s")
        st.caption(f"**Explainability:** Self-Attention + SHAP Values (ϕ_i)")
        st.caption(f"**Port Analytics:** Dynamic Flow & State Attribution")

    # Load Model Engine
    try:
        load_ai_engine()
    except Exception as e:
        st.error(f"Error loading AI model: {e}")
        st.info("Ensure artifacts_v2/attention_world_model.pt exists and dependencies are installed.")
        st.stop()

    # Extract current window sequence
    curr_step = st.session_state.step_idx
    history_df = df_scenario.iloc[curr_step - SEQ_LEN:curr_step]

    # Compute or fetch cached AI inference diagnostics (shared across sessions)
    diag = compute_step_diagnostics(selected_scenario_name, curr_step)
    prediction = diag["prediction"]
    attribution_df = diag["attribution_df"]
    attention_df = diag["attention_df"]
    rollout_df = diag["rollout_df"]
    port_transition_data = diag["port_transition_data"]
    current_row = diag["current_row_dict"]
    current_time_str = diag["current_time_str"]

    # 1. Executive Banner
    render_header(
        scenario_name=selected_scenario_name,
        current_window=current_time_str,
        threat_level=prediction['threat_level']
    )

    # 2. Executive KPI Cards
    render_metrics(prediction=prediction, current_state=current_row)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 3. MITRE ATT&CK Kill-Chain Matrix & Global State Softmax
    render_mitre_matrix(
        predicted_stage=prediction['predicted_stage'],
        stage_probs=prediction['stage_probabilities'],
        rollout_df=rollout_df
    )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 4. Port State-Transition Dynamics & Pipeline
    render_port_analysis(port_transition_data=port_transition_data)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 5. 60-Second Rollout Trajectory Simulation
    render_rollout_view(rollout_df=rollout_df)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 6. Real-Time Telemetry Stream
    render_telemetry_charts(history_df=history_df)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 7. Explainable AI Diagnostics (XAI)
    render_xai_panel(attention_df=attention_df, attribution_df=attribution_df)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 8. Incident Feed & Automated Response Playbooks
    render_alert_feed(prediction=prediction, current_state=current_row)

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
