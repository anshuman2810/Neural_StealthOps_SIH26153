import streamlit as st
import pandas as pd

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def render_rollout_view(rollout_df: pd.DataFrame):
    """
    Renders the 60-second forward simulation rollout trajectory:
    1. Time-Series Infiltration Probability Score curve (+10s to +60s)
    2. Projected Model States and Confidence Distribution across future horizons
    """
    st.markdown("### 60-Second Autoregressive World Model Rollout Simulation")
    st.caption(r"State-Transition Dynamics $P(S_{t+1} \mid S_t)$: Recursively propagates predicted states forward to forecast infiltration probability and kill-chain escalation before compromise completes.")

    if rollout_df.empty:
        st.info("No rollout simulation data available.")
        return

    col1, col2 = st.columns([3, 2])

    with col1:
        if HAS_PLOTLY:
            fig = go.Figure()

            # Area trace for threat trajectory
            fig.add_trace(
                go.Scatter(
                    x=rollout_df['seconds_ahead'],
                    y=rollout_df['risk_pct'],
                    mode='lines+markers+text',
                    name='Infiltration Probability',
                    line=dict(color='#dc2626', width=2.5),
                    fill='tozeroy',
                    fillcolor='rgba(220, 38, 38, 0.08)',
                    marker=dict(size=7, color='#dc2626'),
                    text=[f"{s}" for s in rollout_df['predicted_stage']],
                    textposition='top center',
                    textfont=dict(color='#1e293b', size=10)
                )
            )

            # Critical threshold line at 50%
            fig.add_hline(
                y=50.0,
                line_dash="dash",
                line_color="#d97706",
                annotation_text="Critical Action Threshold (50%)",
                annotation_position="bottom right",
                annotation_font_color="#d97706"
            )

            fig.update_layout(
                title="<b>World Model Time-Series Infiltration Probability & State Progression (+10s to +60s)</b>",
                title_font=dict(color="#0f172a", size=13),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#f8fafc",
                margin=dict(l=40, r=40, t=50, b=40),
                xaxis=dict(
                    title=dict(text="Forward Simulation Horizon (Seconds Ahead)", font=dict(color="#475569")),
                    tickvals=[10, 20, 30, 40, 50, 60],
                    ticktext=["+10s", "+20s", "+30s", "+40s", "+50s", "+60s"],
                    tickfont=dict(color="#475569"),
                    showgrid=True,
                    gridcolor="#e2e8f0"
                ),
                yaxis=dict(
                    title=dict(text="Infiltration Probability (%)", font=dict(color="#475569")),
                    range=[0, 105],
                    tickfont=dict(color="#475569"),
                    showgrid=True,
                    gridcolor="#e2e8f0"
                ),
                height=320
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(rollout_df.set_index('seconds_ahead')['risk_pct'])

    with col2:
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <div style="color: #0f172a; font-weight: 700; font-size: 0.92rem;">
                    World Model Future Simulation Summary
                </div>
                <div style="color: #64748b; font-size: 0.72rem; font-weight: 600;">
                    +10s to +60s Horizon
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        display_df = pd.DataFrame({
            'Horizon': [f"+{int(row['seconds_ahead'])}s" for _, row in rollout_df.iterrows()],
            'Infiltration Prob': [round(float(row['risk_pct']), 1) for _, row in rollout_df.iterrows()],
            'Model State': [str(row['predicted_stage']) for _, row in rollout_df.iterrows()],
            'State Prob': [round(float(row.get('stage_confidence_pct', 0.0)), 1) for _, row in rollout_df.iterrows()]
        })

        st.dataframe(
            display_df,
            column_config={
                'Horizon': st.column_config.TextColumn('Horizon', width='small'),
                'Infiltration Prob': st.column_config.ProgressColumn(
                    'Infiltration Prob',
                    format='%.1f%%',
                    min_value=0.0,
                    max_value=100.0,
                    width='medium'
                ),
                'Model State': st.column_config.TextColumn('Model State', width='medium'),
                'State Prob': st.column_config.ProgressColumn(
                    'State Prob',
                    format='%.1f%%',
                    min_value=0.0,
                    max_value=100.0,
                    width='small'
                )
            },
            use_container_width=True,
            hide_index=True,
            height=280
        )

        st.caption("World Model Latent Trajectory: Rather than repeatedly reporting static classifications, the network state transitions are autoregressively propagated through the learned latent space to simulate future attacker progression.")
