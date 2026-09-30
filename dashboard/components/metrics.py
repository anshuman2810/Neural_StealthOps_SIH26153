from typing import Dict, Any
import streamlit as st

def render_metrics(prediction: Dict[str, Any], current_state: Dict[str, Any]):
    """Renders executive KPI cards with enhanced contrast and elevation in light theme."""
    risk_10 = prediction.get("risk_10s", 0.0) * 100.0
    risk_30 = prediction.get("risk_30s", 0.0) * 100.0
    risk_60 = prediction.get("risk_60s", 0.0) * 100.0
    stage = prediction.get("predicted_stage", "Normal")
    confidence = prediction.get("stage_confidence", 0.0) * 100.0
    threat_level = prediction.get("threat_level", "NORMAL")

    cols = st.columns(5)

    def color_for_risk(r: float) -> str:
        if r < 20.0:
            return "#059669"  # emerald-600
        elif r < 60.0:
            return "#d97706"  # amber-600
        elif r < 85.0:
            return "#ea580c"  # orange-600
        return "#dc2626"      # red-600

    # Card 1: World Model Threat Level
    with cols[0]:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="color: #64748b; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">World Model Threat Level</div>
                <div style="color: {color_for_risk(prediction.get('max_risk', 0.0) * 100.0)}; font-size: 1.45rem; font-weight: 800; margin: 8px 0;">
                    {threat_level}
                </div>
                <div style="color: #64748b; font-size: 0.72rem; font-weight: 500;">Global Network State</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Card 2: Probability at +10s
    with cols[1]:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="color: #64748b; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">Infiltration Prob (+10s)</div>
                <div style="color: {color_for_risk(risk_10)}; font-size: 1.45rem; font-weight: 800; margin: 8px 0;">
                    {risk_10:.1f}%
                </div>
                <div style="color: #64748b; font-size: 0.72rem; font-weight: 500;">Immediate Next Window</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Card 3: Probability at +30s (Primary Benchmark Horizon)
    with cols[2]:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 2.5px solid #2563eb; border-radius: 8px; padding: 13px; text-align: center; box-shadow: 0 3px 8px rgba(37,99,235,0.16);">
                <div style="color: #2563eb; font-size: 0.74rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em;">Infiltration Prob (+30s)</div>
                <div style="color: {color_for_risk(risk_30)}; font-size: 1.45rem; font-weight: 800; margin: 8px 0;">
                    {risk_30:.1f}%
                </div>
                <div style="color: #1e3a8a; font-size: 0.72rem; font-weight: 700;">Primary Advance Lead</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Card 4: Probability at +60s
    with cols[3]:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="color: #64748b; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">Infiltration Prob (+60s)</div>
                <div style="color: {color_for_risk(risk_60)}; font-size: 1.45rem; font-weight: 800; margin: 8px 0;">
                    {risk_60:.1f}%
                </div>
                <div style="color: #64748b; font-size: 0.72rem; font-weight: 500;">Extended 1-Min Horizon</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Card 5: Forecasted Model State
    with cols[4]:
        stage_color = "#059669" if stage == "Normal" else "#dc2626"
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="color: #64748b; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">Forecasted Model State</div>
                <div style="color: {stage_color}; font-size: 1.15rem; font-weight: 800; margin: 8px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{stage}">
                    {stage}
                </div>
                <div style="color: #64748b; font-size: 0.72rem; font-weight: 500;">State Prob: {confidence:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
