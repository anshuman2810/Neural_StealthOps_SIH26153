import streamlit as st
from typing import Dict, Any

def render_mitre_matrix(predicted_stage: str, stage_probs: Dict[str, float]):
    """Renders the MITRE ATT&CK Kill-Chain progression matrix."""
    st.markdown("### 🎯 MITRE ATT&CK® Kill-Chain Progression Matrix")

    stages_meta = [
        ("Normal", "Baseline", "Passive benign traffic profile"),
        ("Initial Access", "Entry Attempt", "Web exploit / Brute Force (XSS, SQLi)"),
        ("Credential Access", "Authentication", "Password spraying (FTP, SSH)"),
        ("Lateral Movement", "Internal Pivot", "Host-to-host infiltration / Port scan"),
        ("Command and Control", "Beaconing", "Botnet heartbeat / External C2 channel"),
        ("Impact", "Disruption", "Volumetric DDoS / Resource exhaustion")
    ]

    cols = st.columns(len(stages_meta))

    for col, (stage_name, subtitle, desc) in zip(cols, stages_meta):
        is_active = (predicted_stage == stage_name)
        prob = stage_probs.get(stage_name, 0.0) * 100.0

        if is_active:
            if stage_name == "Normal":
                border_color = "#10b981"
                bg_color = "rgba(16, 185, 129, 0.15)"
                title_color = "#34d399"
                badge = "ACTIVE BASELINE"
            else:
                border_color = "#ef4444"
                bg_color = "rgba(239, 68, 68, 0.2)"
                title_color = "#f87171"
                badge = "THREAT DETECTED"
        else:
            border_color = "#334155"
            bg_color = "#0f172a"
            title_color = "#94a3b8"
            badge = f"{prob:.1f}% prob"

        with col:
            st.markdown(
                f"""
                <div style="background: {bg_color}; border: 2px solid {border_color}; 
                            border-radius: 8px; padding: 12px 10px; min-height: 125px; text-align: center;
                            box-shadow: {'0 0 12px ' + border_color if is_active else 'none'};">
                    <div style="font-size: 0.7rem; font-weight: 700; color: {border_color}; text-transform: uppercase;">
                        {badge}
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: {title_color}; margin: 6px 0 2px 0;">
                        {stage_name}
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">
                        {subtitle}
                    </div>
                    <div style="font-size: 0.7rem; color: #cbd5e1; margin-top: 6px; line-height: 1.2;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
