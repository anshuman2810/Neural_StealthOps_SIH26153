import streamlit as st
import pandas as pd
import numpy as np

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def render_telemetry_charts(history_df: pd.DataFrame):
    """Renders real-time telemetry time-series charts for the active sequence window in light theme."""
    st.markdown("### Real-Time Network Telemetry Stream (Past 2 Minutes)")

    if history_df.empty:
        st.info("Awaiting telemetry data...")
        return

    # Add friendly window time or step offset
    df_plot = history_df.copy().reset_index(drop=True)
    if 'window' in df_plot.columns:
        df_plot['time_label'] = pd.to_datetime(df_plot['window']).dt.strftime('%H:%M:%S')
    else:
        df_plot['time_label'] = [f"t-{10*(len(df_plot)-1-i)}s" for i in range(len(df_plot))]

    col1, col2 = st.columns(2)

    if HAS_PLOTLY:
        # Chart 1: Flow & Packet Rates
        with col1:
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            fig1.add_trace(
                go.Scatter(
                    x=df_plot['time_label'],
                    y=df_plot['flow_count'],
                    name="Flows / 10s",
                    line=dict(color="#2563eb", width=2.5),
                    mode="lines+markers"
                ),
                secondary_y=False
            )
            fig1.add_trace(
                go.Scatter(
                    x=df_plot['time_label'],
                    y=df_plot['total_packets'],
                    name="Total Packets",
                    line=dict(color="#4f46e5", width=2, dash="dot"),
                    mode="lines"
                ),
                secondary_y=True
            )
            fig1.update_layout(
                title="<b>Traffic Volume Velocity</b>",
                title_font=dict(color="#0f172a", size=13),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#f8fafc",
                margin=dict(l=40, r=40, t=40, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#334155")),
                xaxis=dict(showgrid=True, gridcolor="#e2e8f0", tickfont=dict(color="#475569")),
                yaxis=dict(title=dict(text="Flow Count", font=dict(color="#2563eb")), tickfont=dict(color="#475569"), showgrid=True, gridcolor="#e2e8f0"),
                yaxis2=dict(title=dict(text="Packet Volume", font=dict(color="#4f46e5")), tickfont=dict(color="#475569"), showgrid=False),
                height=300
            )
            st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: TCP Flag Breakdown & Port Entropy
        with col2:
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            flag_cols = [
                ('mean_SYN Flag Cnt', 'SYN Flag Rate', '#d97706'),
                ('mean_RST Flag Cnt', 'RST Flag Rate', '#dc2626'),
                ('mean_ACK Flag Cnt', 'ACK Flag Rate', '#059669')
            ]
            for col_name, label, color in flag_cols:
                if col_name in df_plot.columns:
                    fig2.add_trace(
                        go.Scatter(
                            x=df_plot['time_label'],
                            y=df_plot[col_name],
                            name=label,
                            line=dict(color=color, width=2),
                            mode="lines"
                        ),
                        secondary_y=False
                    )

            if 'port_entropy' in df_plot.columns:
                fig2.add_trace(
                    go.Scatter(
                        x=df_plot['time_label'],
                        y=df_plot['port_entropy'],
                        name="Port Entropy",
                        line=dict(color="#7c3aed", width=2.5, dash="dash"),
                        mode="lines"
                    ),
                    secondary_y=True
                )

            fig2.update_layout(
                title="<b>TCP Control Flags & Port Entropy</b>",
                title_font=dict(color="#0f172a", size=13),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#f8fafc",
                margin=dict(l=40, r=40, t=40, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#334155")),
                xaxis=dict(showgrid=True, gridcolor="#e2e8f0", tickfont=dict(color="#475569")),
                yaxis=dict(title=dict(text="Mean Flag Rate", font=dict(color="#d97706")), tickfont=dict(color="#475569"), showgrid=True, gridcolor="#e2e8f0"),
                yaxis2=dict(title=dict(text="Port Entropy (bits)", font=dict(color="#7c3aed")), tickfont=dict(color="#475569"), showgrid=False),
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.line_chart(df_plot.set_index('time_label')[['flow_count', 'total_packets']])
