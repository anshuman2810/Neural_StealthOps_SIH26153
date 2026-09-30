import streamlit as st

def render_header(scenario_name: str, current_window: str, threat_level: str):
    """Renders the executive SOC header banner in an enterprise light theme with enhanced contrast."""
    theme_map = {
        "NORMAL": {"bg": "#ecfdf5", "border": "#6ee7b7", "text": "#047857"},
        "ELEVATED": {"bg": "#fffbeb", "border": "#fcd34d", "text": "#b45309"},
        "HIGH": {"bg": "#fff7ed", "border": "#fdba74", "text": "#c2410c"},
        "CRITICAL": {"bg": "#fef2f2", "border": "#fca5a5", "text": "#b91c1c"}
    }
    status_theme = theme_map.get(threat_level, {"bg": "#eff6ff", "border": "#93c5fd", "text": "#1d4ed8"})

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; 
                    padding: 16px 22px; margin-bottom: 18px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                <div>
                    <h2 style="color: #0f172a; margin: 0; font-size: 1.45rem; font-weight: 700; letter-spacing: -0.3px;">
                        Predictive Network World Model — SOC Telemetry & Forecast Console
                    </h2>
                    <p style="color: #475569; margin: 4px 0 0 0; font-size: 0.88rem;">
                        Autonomous 10s Network State Simulation & Multi-Horizon ATT&CK Trajectory Forecasting
                    </p>
                </div>
                <div style="display: flex; gap: 12px; align-items: center;">
                    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 12px; text-align: right;">
                        <span style="color: #64748b; font-size: 0.70rem; text-transform: uppercase; font-weight: 700; display: block;">Active Scenario</span>
                        <div style="color: #0f172a; font-weight: 700; font-size: 0.88rem;">{scenario_name}</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 12px; text-align: right;">
                        <span style="color: #64748b; font-size: 0.70rem; text-transform: uppercase; font-weight: 700; display: block;">Window Time</span>
                        <div style="color: #0f172a; font-weight: 700; font-size: 0.88rem;">{current_window}</div>
                    </div>
                    <div style="background: {status_theme['bg']}; border: 1.5px solid {status_theme['border']}; border-radius: 6px; padding: 6px 14px; text-align: center;">
                        <span style="color: {status_theme['text']}; font-size: 0.70rem; text-transform: uppercase; font-weight: 800; display: block;">Status</span>
                        <div style="color: {status_theme['text']}; font-weight: 800; font-size: 0.95rem; letter-spacing: 0.5px;">{threat_level}</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
