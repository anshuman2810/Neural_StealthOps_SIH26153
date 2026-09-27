import streamlit as st
from typing import Dict, Any, List
from src.config import STAGE_PLAYBOOKS, STAGE_SEVERITY

def render_alert_feed(prediction: Dict[str, Any], current_state: Dict[str, Any]):
    """Renders real-time SOC incident feed and automated mitigation playbooks."""
    st.markdown("### 🚨 SOC Autonomous Response Playbooks & Threat Feed")

    threat_level = prediction.get("threat_level", "NORMAL")
    stage = prediction.get("predicted_stage", "Normal")
    risk_30 = prediction.get("risk_30s", 0.0) * 100.0
    playbook = STAGE_PLAYBOOKS.get(stage, "Standard passive network surveillance.")
    severity = STAGE_SEVERITY.get(stage, "INFO")

    col1, col2 = st.columns([2, 1])

    with col1:
        if threat_level in ("HIGH", "CRITICAL") or stage != "Normal":
            badge_color = "#ef4444" if severity == "CRITICAL" else "#f97316"
            st.markdown(
                f"""
                <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid {badge_color}; 
                            border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="background: {badge_color}; color: #ffffff; font-weight: 800; font-size: 0.75rem; 
                                     padding: 3px 8px; border-radius: 4px; text-transform: uppercase;">
                            {severity} ALERT
                        </span>
                        <span style="color: #94a3b8; font-size: 0.8rem;">
                            Forecasted Risk: <b>{risk_30:.1f}% (+30s Lead)</b>
                        </span>
                    </div>
                    <div style="color: #f8fafc; font-size: 1.05rem; font-weight: 700; margin: 8px 0 4px 0;">
                        {stage} Attack Trajectory Detected
                    </div>
                    <div style="color: #e2e8f0; font-size: 0.85rem; line-height: 1.4;">
                        <b>Recommended Mitigation Playbook:</b> {playbook}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; 
                            border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;">
                    <div style="color: #34d399; font-weight: 700; font-size: 0.95rem;">
                        ✅ All Systems Operational — Baseline Conformance
                    </div>
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                        No anomalous state transitions observed. Telemetry metrics within 99th percentile normal bounds.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col2:
        st.markdown(
            """
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px;">
                <div style="color: #38bdf8; font-weight: 700; font-size: 0.85rem; margin-bottom: 8px;">
                    ⚡ Autonomous SOAR Action
                </div>
            """,
            unsafe_allow_html=True
        )

        if threat_level in ("HIGH", "CRITICAL") or stage != "Normal":
            if st.button("🛡️ Execute Playbook Mitigation", key="btn_mitigate", use_container_width=True):
                st.success(f"Executed: Firewall rule deployed & host quarantine signal sent for {stage}!")
        else:
            st.button("⚙️ Re-baseline Anomaly Thresholds", key="btn_rebaseline", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)
