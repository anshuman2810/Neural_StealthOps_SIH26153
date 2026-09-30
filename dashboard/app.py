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

from src.config import SEQ_LEN, WINDOW_SECONDS
from src.data.scenario_loader import ScenarioLoader
from src.models.predictor import NetworkWorldModelPredictor
from src.explainability.shap_explainer import ShapExplainer
from src.explainability.attention_explainer import AttentionExplainer
from src.simulation.rollout import AutoregressiveRolloutSimulator
from src.simulation.port_engine import PortTelemetryEngine

from dashboard.views import (
    render_landing_page,
    render_threat_engine,
    render_system_management
)

# Configure Streamlit page
st.set_page_config(
    page_title="NeuralOps — Threat Forecasting & System Management Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom high-contrast light enterprise styling & glowing LED animations
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

        /* Pulsing LED animations for Health Indicators */
        @keyframes pulse-green {
            0% {
                box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
                transform: scale(0.95);
            }
            70% {
                box-shadow: 0 0 0 8px rgba(34, 197, 94, 0);
                transform: scale(1.05);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
                transform: scale(0.95);
            }
        }
        .blink-dot-green {
            display: inline-block;
            width: 11px;
            height: 11px;
            background-color: #22c55e;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
            animation: pulse-green 1.8s infinite;
        }
        @keyframes pulse-red {
            0% {
                box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
                transform: scale(0.95);
            }
            70% {
                box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
                transform: scale(1.05);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
                transform: scale(0.95);
            }
        }
        .blink-dot-red {
            display: inline-block;
            width: 11px;
            height: 11px;
            background-color: #ef4444;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
            animation: pulse-red 1.5s infinite;
        }

        /* Top Persistent Navigation Bar */
        .top-navbar-container {
            background: #ffffff;
            border: 1.5px solid #cbd5e1;
            border-radius: 10px;
            padding: 10px 18px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
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

def render_top_navigation():
    """Renders the persistent top navigation bar allowing quick navigation and switching between views."""
    current_page = st.session_state.get("current_page", "landing")
    
    col_nav_brand, col_nav_btn1, col_nav_btn2, col_nav_btn3 = st.columns([2.5, 1.2, 1.6, 1.6])

    with col_nav_brand:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; height: 100%; padding-top: 4px;">
                <span style="font-weight: 800; font-size: 1.15rem; color: #0f172a; letter-spacing: -0.3px;">🛡️ Team NeuralOps</span>
                <span style="background: #e2e8f0; color: #475569; font-size: 0.72rem; padding: 2px 7px; border-radius: 4px; font-weight: 700;">SIH-26153</span>
                <span style="color: #64748b; font-size: 0.82rem; font-weight: 600;">DIAT Pune</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_nav_btn1:
        if st.button("🏠 Home / Landing", key="nav_home", use_container_width=True):
            st.session_state.current_page = "landing"
            st.rerun()

    with col_nav_btn2:
        is_threat_active = current_page == "threat_engine"
        btn_label = "🧠 Threat Engine ●" if is_threat_active else "🧠 Threat Engine"
        if st.button(btn_label, key="nav_threat", use_container_width=True):
            st.session_state.current_page = "threat_engine"
            st.rerun()

    with col_nav_btn3:
        is_mgmt_active = current_page == "system_management"
        btn_label = "🖥️ System Health ●" if is_mgmt_active else "🖥️ System Health"
        if st.button(btn_label, key="nav_mgmt", use_container_width=True):
            st.session_state.current_page = "system_management"
            st.rerun()

    st.markdown("<hr style='border: 0.5px solid #cbd5e1; margin: 8px 0 16px 0;'>", unsafe_allow_html=True)

def main():
    # Initialize session state page routing
    if "current_page" not in st.session_state:
        st.session_state.current_page = "landing"

    loader = ScenarioLoader()

    # If inside either dashboard, render the top persistent navigation bar
    if st.session_state.current_page != "landing":
        render_top_navigation()

    # Route based on current page
    if st.session_state.current_page == "landing":
        render_landing_page()

    elif st.session_state.current_page == "threat_engine":
        render_threat_engine(
            loader=loader,
            get_cached_scenario=get_cached_scenario,
            compute_step_diagnostics=compute_step_diagnostics,
            load_ai_engine=load_ai_engine
        )

    elif st.session_state.current_page == "system_management":
        render_system_management()

if __name__ == "__main__":
    main()
