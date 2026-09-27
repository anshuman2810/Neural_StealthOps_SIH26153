from typing import Dict, Any
import streamlit as st

def render_metrics(prediction: Dict[str, Any], current_state: Dict[str, Any]):
    """Renders executive KPI cards with direct multi-horizon attack forecasts."""
    risk_10 = prediction.get("risk_10s", 0.0) * 100.0
    risk_30 = prediction.get("risk_30s", 0.0) * 100.0
    risk_60 = prediction.get("risk_60s", 0.0) * 100.0
    stage = prediction.get("predicted_stage", "Normal")
    confidence = prediction.get("stage_confidence", 0.0) * 100.0
    threat_level = prediction.get("threat_level", "NORMAL")

    cols = st.columns(5)

    def color_for_risk(r: float) -> str:
        if r < 20.0:
            return "#10b981"  # green
        elif r < 60.0:
            return "#f59e0b"  # amber
        elif r < 85.0:
            return "#f97316"  # orange
        return "#ef4444"      # red

    # Card 1: Threat Posture
    with cols[0]:
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Current Threat Level</div>
                <div style="color: {color_for_risk(prediction.get('max_risk', 0.0) * 100.0)}; font-size: 1.5rem; font-weight: 800; margin: 8px 0;">
                    {threat_level}
                </div>
                <div style="color: #64748b; font-size: 0.75rem;">Global Network State</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Card 2: Risk +10s
    with cols[1]:
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Risk at +10s Ahead</div>
                <div style="color: {color_for_risk(risk_10)}; font-size: 1.5rem; font-weight: 800; margin: 8px 0;">
                    {risk_10:.1f}%
                </div>
                <div style="color: #64748b; font-size: 0.75rem;">Next 10-second Window</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Card 3: Risk +30s (Primary Benchmark Horizon)
    with cols[2]:
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #38bdf8; border-radius: 8px; padding: 14px; text-align: center; box-shadow: 0 0 10px rgba(56, 189, 248, 0.15);">
                <div style="color: #38bdf8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Risk at +30s (Primary)</div>
                <div style="color: {color_for_risk(risk_30)}; font-size: 1.5rem; font-weight: 800; margin: 8px 0;">
                    {risk_30:.1f}%
                </div>
                <div style="color: #94a3b8; font-size: 0.75rem;">Advance Warning Lead</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Card 4: Risk +60s
    with cols[3]:
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Risk at +60s Ahead</div>
                <div style="color: {color_for_risk(risk_60)}; font-size: 1.5rem; font-weight: 800; margin: 8px 0;">
                    {risk_60:.1f}%
                </div>
                <div style="color: #64748b; font-size: 0.75rem;">Extended 1-Min Horizon</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Card 5: MITRE Stage Forecast
    with cols[4]:
        stage_color = "#38bdf8" if stage == "Normal" else "#f43f5e"
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Forecasted ATT&CK Stage</div>
                <div style="color: {stage_color}; font-size: 1.15rem; font-weight: 800; margin: 10px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{stage}">
                    {stage}
                </div>
                <div style="color: #64748b; font-size: 0.75rem;">Confidence: {confidence:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
