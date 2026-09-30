import streamlit as st
import pandas as pd
from typing import Dict, Any

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def render_mitre_matrix(predicted_stage: str, stage_probs: Dict[str, float], rollout_df: pd.DataFrame = None):
    """
    Renders the World Model State-Transition Dynamics:
    1. 7 Model States Kill-Chain Progression Cards
    2. Explicit Probability Distribution over the 7 Model States P(S_{t+1} | S_t)
    """
    st.markdown("### World Model State Dynamics: MITRE ATT&CK Kill-Chain Progression")
    st.caption(r"State-Transition Dynamics $P(S_{t+1} \mid S_t)$: Categorical probability distribution across all 7 operational model states.")

    # All 7 Model States defined in src/config.py
    stages_meta = [
        ("Normal", "Baseline", "Passive benign traffic profile", "#059669"),
        ("Initial Access", "Entry Attempt", "Web exploit / Brute Force (XSS, SQLi)", "#0284c7"),
        ("Credential Access", "Authentication", "Password spraying (FTP, SSH)", "#d97706"),
        ("Lateral Movement", "Internal Pivot", "Host-to-host infiltration / Port scan", "#ea580c"),
        ("Command and Control", "Beaconing", "Botnet heartbeat / External C2 channel", "#7c3aed"),
        ("Impact", "Disruption", "Volumetric DDoS / Resource exhaustion", "#dc2626"),
        ("Other Malicious", "Anomaly", "Unclassified anomalous attack flow", "#e11d48")
    ]

    # Row 1: 7 Model State Cards
    cols = st.columns(len(stages_meta))

    for col, (stage_name, subtitle, desc, theme_color) in zip(cols, stages_meta):
        is_active = (predicted_stage == stage_name)
        prob = stage_probs.get(stage_name, 0.0) * 100.0

        if is_active:
            border_color = theme_color
            bg_color = f"{theme_color}0d"
            title_color = "#0f172a"
            badge = "ACTIVE STATE"
            shadow = f"box-shadow: 0 2px 6px {theme_color}33;"
        else:
            border_color = "#cbd5e1"
            bg_color = "#ffffff"
            title_color = "#1e293b"
            badge = f"{prob:.1f}% prob"
            shadow = "box-shadow: 0 1px 3px rgba(0,0,0,0.05);"

        with col:
            st.markdown(
                f"""
                <div style="background: {bg_color}; border: 2px solid {border_color}; 
                            border-radius: 8px; padding: 10px 8px; min-height: 135px; text-align: center; {shadow}">
                    <div style="font-size: 0.70rem; font-weight: 800; color: {border_color}; text-transform: uppercase;">
                        {badge}
                    </div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {title_color}; margin: 5px 0 2px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{stage_name}">
                        {stage_name}
                    </div>
                    <div style="font-size: 0.70rem; color: #64748b; font-weight: 600;">
                        {subtitle}
                    </div>
                    <div style="font-size: 0.68rem; color: #64748b; margin-top: 5px; line-height: 1.2;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Row 2: Explicit Probability Distribution Chart & Table
    col_dist, col_table = st.columns([1.6, 1.0])

    with col_dist:
        if HAS_PLOTLY:
            stage_names = [s[0] for s in stages_meta]
            prob_values = [stage_probs.get(s, 0.0) * 100.0 for s in stage_names]
            colors = [s[3] for s in stages_meta]

            fig_p = go.Figure()
            fig_p.add_trace(
                go.Bar(
                    y=stage_names[::-1],
                    x=prob_values[::-1],
                    orientation='h',
                    marker=dict(
                        color=colors[::-1],
                        line=dict(color='#cbd5e1', width=0.5)
                    ),
                    text=[f"{p:.1f}%" for p in prob_values[::-1]],
                    textposition='outside',
                    textfont=dict(color='#1e293b', size=11)
                )
            )

            fig_p.update_layout(
                title="<b>World Model Probability Distribution over Future Model States: P(S_{t+1} | S_t)</b>",
                title_font=dict(color="#0f172a", size=13),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#f8fafc",
                margin=dict(l=140, r=40, t=40, b=20),
                xaxis=dict(
                    title=dict(text="Probability (%)", font=dict(color="#475569")),
                    range=[0, max(max(prob_values) * 1.2, 105)],
                    showgrid=True,
                    gridcolor="#e2e8f0",
                    tickfont=dict(color="#475569")
                ),
                yaxis=dict(tickfont=dict(color="#334155", size=10), showgrid=False),
                height=270
            )
            st.plotly_chart(fig_p, use_container_width=True)

    with col_table:
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <div style="color: #0f172a; font-weight: 700; font-size: 0.92rem;">
                    Model States Probability Breakdown
                </div>
                <div style="color: #64748b; font-size: 0.72rem; font-weight: 600;">
                    P(S<sub>t+1</sub> | S<sub>t</sub>)
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        df_p = pd.DataFrame({
            'Model State': [f"{s[0]} (Active)" if predicted_stage == s[0] else s[0] for s in stages_meta],
            'Probability': [round(stage_probs.get(s[0], 0.0) * 100.0, 2) for s in stages_meta],
            'Classification': ["Baseline" if s[0] == "Normal" else "Malicious" for s in stages_meta]
        })

        st.dataframe(
            df_p,
            column_config={
                'Model State': st.column_config.TextColumn('Model State', width='medium'),
                'Probability': st.column_config.ProgressColumn(
                    'Probability',
                    format='%.2f%%',
                    min_value=0.0,
                    max_value=100.0,
                    width='medium'
                ),
                'Classification': st.column_config.TextColumn('Classification', width='small')
            },
            use_container_width=True,
            hide_index=True,
            height=270
        )
        st.caption("World Model Softmax: Rather than outputting a hard threshold, the world model outputs a continuous probability distribution across all 7 operational states.")
