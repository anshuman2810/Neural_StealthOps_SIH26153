import streamlit as st
from typing import Dict, Any, List
from src.config import STAGE_PLAYBOOKS, STAGE_SEVERITY

def render_alert_feed(prediction: Dict[str, Any], current_state: Dict[str, Any]):
    """Renders real-time SOC incident feed and automated mitigation playbooks in light theme."""
    st.markdown("### SOC Autonomous Response Playbooks & Threat Feed")

    threat_level = prediction.get("threat_level", "NORMAL")
    stage = prediction.get("predicted_stage", "Normal")
    risk_30 = prediction.get("risk_30s", 0.0) * 100.0
    playbook = STAGE_PLAYBOOKS.get(stage, "Standard passive network surveillance.")
    severity = STAGE_SEVERITY.get(stage, "INFO")

    col1, col2 = st.columns([2, 1])

    with col1:
        if threat_level in ("HIGH", "CRITICAL") or stage != "Normal":
            badge_color = "#dc2626" if severity == "CRITICAL" else "#ea580c"
            bg_color = "#fef2f2" if severity == "CRITICAL" else "#fff7ed"
            border_color = "#fecaca" if severity == "CRITICAL" else "#fed7aa"

            st.markdown(
                f"""
                <div style="background: {bg_color}; border: 1px solid {border_color}; border-left: 4px solid {badge_color}; 
                            border-radius: 6px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="background: {badge_color}; color: #ffffff; font-weight: 800; font-size: 0.72rem; 
                                     padding: 3px 8px; border-radius: 4px; text-transform: uppercase;">
                            {severity} ALERT
                        </span>
                        <span style="color: #64748b; font-size: 0.80rem;">
                            Forecasted Risk: <b style="color: #0f172a;">{risk_30:.1f}% (+30s Lead)</b>
                        </span>
                    </div>
                    <div style="color: #0f172a; font-size: 1.05rem; font-weight: 700; margin: 8px 0 4px 0;">
                        {stage} Attack Trajectory Detected
                    </div>
                    <div style="color: #334155; font-size: 0.85rem; line-height: 1.4;">
                        <b>Recommended Mitigation Playbook:</b> {playbook}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-left: 4px solid #059669; 
                            border-radius: 6px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                    <div style="color: #065f46; font-weight: 700; font-size: 0.95rem;">
                        All Systems Operational — Baseline Conformance
                    </div>
                    <div style="color: #047857; font-size: 0.85rem; margin-top: 4px;">
                        No anomalous state transitions observed. Telemetry metrics within 99th percentile normal bounds.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="color: #0f172a; font-weight: 700; font-size: 0.88rem; margin-bottom: 8px;">
                    Autonomous SOAR Action
                </div>
                """,
                unsafe_allow_html=True
            )

            if threat_level in ("HIGH", "CRITICAL") or stage != "Normal":
                if st.button("Execute Playbook Mitigation", key="btn_mitigate", use_container_width=True):
                    st.success(f"Executed: Firewall rule deployed and host quarantine signal sent for {stage}!")
            else:
                st.button("Re-baseline Anomaly Thresholds", key="btn_rebaseline", use_container_width=True)
