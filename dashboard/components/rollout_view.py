import streamlit as st
import pandas as pd

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def render_rollout_view(rollout_df: pd.DataFrame):
    """Renders the 60-second forward simulation rollout trajectory."""
    st.markdown("### 🔮 60-Second Autoregressive World Model Rollout Simulation")

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
                    name='Projected Threat Risk',
                    line=dict(color='#ef4444', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(239, 68, 68, 0.15)',
                    marker=dict(size=8, color='#f87171'),
                    text=[f"{s}" for s in rollout_df['predicted_stage']],
                    textposition='top center',
                    textfont=dict(color='#cbd5e1', size=11)
                )
            )

            # Critical threshold line at 50%
            fig.add_hline(
                y=50.0,
                line_dash="dash",
                line_color="#f59e0b",
                annotation_text="Critical Action Threshold (50%)",
                annotation_position="bottom right",
                annotation_font_color="#f59e0b"
            )

            fig.update_layout(
                title="<b>Projected Attack Risk & Stage Evolution (+10s to +60s)</b>",
                title_font=dict(color="#f8fafc", size=14),
                paper_bgcolor="#1e293b",
                plot_bgcolor="#0f172a",
                margin=dict(l=40, r=40, t=50, b=40),
                xaxis=dict(
                    title=dict(text="Simulation Horizon (Seconds Ahead)", font=dict(color="#cbd5e1")),
                    tickvals=[10, 20, 30, 40, 50, 60],
                    ticktext=["+10s", "+20s", "+30s", "+40s", "+50s", "+60s"],
                    tickfont=dict(color="#94a3b8"),
                    showgrid=True,
                    gridcolor="#334155"
                ),
                yaxis=dict(
                    title=dict(text="Risk Probability (%)", font=dict(color="#cbd5e1")),
                    range=[0, 105],
                    tickfont=dict(color="#94a3b8"),
                    showgrid=True,
                    gridcolor="#334155"
                ),
                height=320
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(rollout_df.set_index('seconds_ahead')['risk_pct'])

    with col2:
        st.markdown(
            """
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 14px; height: 320px; overflow-y: auto;">
                <div style="color: #38bdf8; font-weight: 700; font-size: 0.9rem; margin-bottom: 10px;">
                    Forward Simulation Summary
                </div>
            """,
            unsafe_allow_html=True
        )

        display_df = rollout_df[['seconds_ahead', 'risk_pct', 'predicted_stage']].copy()
        display_df.columns = ['Horizon', 'Forecasted Risk', 'Stage']
        display_df['Horizon'] = display_df['Horizon'].apply(lambda s: f"+{s}s")
        display_df['Forecasted Risk'] = display_df['Forecasted Risk'].apply(lambda r: f"{r:.1f}%")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown(
            """
            <p style="color: #94a3b8; font-size: 0.75rem; margin-top: 8px;">
                💡 <b>World Model Advantage:</b> Rather than repeatedly reporting static classifications, the network state transitions are autoregressively propagated through the learned latent space.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )
