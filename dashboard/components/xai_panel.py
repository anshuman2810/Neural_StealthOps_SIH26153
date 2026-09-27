import streamlit as st
import pandas as pd

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def render_xai_panel(attention_df: pd.DataFrame, attribution_df: pd.DataFrame):
    """Renders the Explainable AI (XAI) panel: Temporal Attention & Feature Attribution."""
    st.markdown("### 🧠 Explainable AI (XAI) & Attribution Diagnostics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ⏳ Temporal Attention Focus (Preceding 12 Windows)")
        if not attention_df.empty and HAS_PLOTLY:
            fig1 = go.Figure()
            fig1.add_trace(
                go.Bar(
                    x=attention_df['time_offset'],
                    y=attention_df['percentage'],
                    marker=dict(
                        color=attention_df['percentage'],
                        colorscale='Blues',
                        line=dict(color='#0284c7', width=1)
                    ),
                    text=[f"{p:.1f}%" for p in attention_df['percentage']],
                    textposition='outside',
                    textfont=dict(color='#cbd5e1', size=10)
                )
            )
            fig1.update_layout(
                title="<b>Attention Weights Across 2-Minute History Buffer</b>",
                title_font=dict(color="#f8fafc", size=13),
                paper_bgcolor="#1e293b",
                plot_bgcolor="#0f172a",
                margin=dict(l=30, r=30, t=40, b=50),
                xaxis=dict(tickangle=-45, tickfont=dict(color="#94a3b8", size=10), showgrid=False),
                yaxis=dict(title=dict(text="Attention Weight (%)", font=dict(color="#94a3b8")), showgrid=True, gridcolor="#334155"),
                height=290
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.caption("Pinpoints exact historical windows where anomalous pre-attack signals emerged.")
        else:
            st.dataframe(attention_df, hide_index=True)

    with col2:
        st.markdown("#### 🔍 Gradient × Input Feature Importance")
        if not attribution_df.empty and HAS_PLOTLY:
            fig2 = go.Figure()
            # Invert order for top-to-bottom horizontal bar chart
            sorted_df = attribution_df.iloc[::-1]

            fig2.add_trace(
                go.Bar(
                    y=sorted_df['feature'],
                    x=sorted_df['relative_pct'],
                    orientation='h',
                    marker=dict(
                        color=sorted_df['relative_pct'],
                        colorscale='YlOrRd',
                        line=dict(color='#e11d48', width=1)
                    ),
                    text=[f"{p:.1f}%" for p in sorted_df['relative_pct']],
                    textposition='outside',
                    textfont=dict(color='#cbd5e1', size=10)
                )
            )
            fig2.update_layout(
                title="<b>Top Telemetry Signals Driving Risk Forecast</b>",
                title_font=dict(color="#f8fafc", size=13),
                paper_bgcolor="#1e293b",
                plot_bgcolor="#0f172a",
                margin=dict(l=140, r=40, t=40, b=30),
                xaxis=dict(title=dict(text="Attribution Contribution (%)", font=dict(color="#94a3b8")), showgrid=True, gridcolor="#334155"),
                yaxis=dict(tickfont=dict(color="#cbd5e1", size=10), showgrid=False),
                height=290
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.caption("Ranks the physical network telemetry metrics that caused the risk model to fire.")
        else:
            st.dataframe(attribution_df, hide_index=True)
