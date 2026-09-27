import streamlit as st

def render_header(scenario_name: str, current_window: str, threat_level: str):
    """Renders the top executive SOC header banner."""
    color_map = {
        "NORMAL": "#10b981",    # Emerald
        "ELEVATED": "#f59e0b",  # Amber
        "HIGH": "#f97316",      # Orange
        "CRITICAL": "#ef4444"   # Red
    }
    status_color = color_map.get(threat_level, "#3b82f6")

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
                    border: 1px solid #334155; border-radius: 10px; padding: 18px 24px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h2 style="color: #f8fafc; margin: 0; font-size: 1.6rem; font-weight: 700; letter-spacing: -0.5px;">
                        🛡️ Predictive Network World Model — SOC Telemetry & Forecast Console
                    </h2>
                    <p style="color: #94a3b8; margin: 6px 0 0 0; font-size: 0.95rem;">
                        Autonomous 10s Network State Simulation & Multi-Horizon ATT&CK Trajectory Forecasting
                    </p>
                </div>
                <div style="display: flex; gap: 15px; align-items: center; margin-top: 10px;">
                    <div style="background: #020617; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; text-align: right;">
                        <span style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">Active Scenario</span>
                        <div style="color: #38bdf8; font-weight: 600; font-size: 0.9rem;">{scenario_name}</div>
                    </div>
                    <div style="background: #020617; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; text-align: right;">
                        <span style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">Window Time</span>
                        <div style="color: #e2e8f0; font-weight: 600; font-size: 0.9rem;">{current_window}</div>
                    </div>
                    <div style="background: {status_color}22; border: 1px solid {status_color}; border-radius: 6px; padding: 6px 14px; text-align: center;">
                        <span style="color: {status_color}; font-size: 0.75rem; text-transform: uppercase; font-weight: 700;">Status</span>
                        <div style="color: {status_color}; font-weight: 800; font-size: 1.05rem; letter-spacing: 0.5px;">{threat_level}</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
