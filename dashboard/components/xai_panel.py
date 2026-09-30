import streamlit as st
import pandas as pd

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def render_xai_panel(attention_df: pd.DataFrame, attribution_df: pd.DataFrame):
    """
    Renders the World Model Explainable AI (XAI) panel in light theme:
    1. Temporal Attention Weights across Historical Windows (WHEN)
    2. SHAP Values (Shapley Additive Explanations) Feature Attribution (WHAT)
    """
    st.markdown("### World Model Explainability: Attention Weights & SHAP Values")
    st.caption("Interpretable decision support: Temporal attention weights identify trigger windows; SHAP values quantify feature contributions.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### World Model Temporal Attention Focus (Preceding 12 Windows)")
        if not attention_df.empty and HAS_PLOTLY:
            fig1 = go.Figure()
            fig1.add_trace(
                go.Bar(
                    x=attention_df['time_offset'],
                    y=attention_df['percentage'],
                    marker=dict(
                        color=attention_df['percentage'],
                        colorscale='Blues',
                        line=dict(color='#2563eb', width=1)
                    ),
                    text=[f"{p:.1f}%" for p in attention_df['percentage']],
                    textposition='outside',
                    textfont=dict(color='#1e293b', size=10)
                )
            )
            fig1.update_layout(
                title="<b>Self-Attention Weights Across 2-Minute History Buffer</b>",
                title_font=dict(color="#0f172a", size=13),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#f8fafc",
                margin=dict(l=30, r=30, t=40, b=50),
                xaxis=dict(tickangle=-45, tickfont=dict(color="#475569", size=10), showgrid=False),
                yaxis=dict(title=dict(text="Attention Weight (%)", font=dict(color="#475569")), showgrid=True, gridcolor="#e2e8f0", tickfont=dict(color="#475569")),
                height=300
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.caption("Pinpoints exact historical windows where anomalous pre-attack signals emerged.")
        else:
            st.dataframe(attention_df, hide_index=True)

    with col2:
        st.markdown("#### SHAP Feature Attribution: SHAP Values (ϕ_i)")
        if not attribution_df.empty and HAS_PLOTLY:
            fig2 = go.Figure()
            sorted_df = attribution_df.iloc[::-1]

            val_col = 'shap_value' if 'shap_value' in sorted_df.columns else ('importance' if 'importance' in sorted_df.columns else 'relative_pct')
            pct_col = 'relative_pct' if 'relative_pct' in sorted_df.columns else val_col

            fig2.add_trace(
                go.Bar(
                    y=sorted_df['feature'],
                    x=sorted_df[pct_col],
                    orientation='h',
                    marker=dict(
                        color=sorted_df[pct_col],
                        colorscale='OrRd',
                        line=dict(color='#dc2626', width=1)
                    ),
                    text=[f"{p:.1f}%" for p in sorted_df[pct_col]],
                    textposition='outside',
                    textfont=dict(color='#1e293b', size=10)
                )
            )
            fig2.update_layout(
                title="<b>SHAP Values Driving World Model Infiltration Probability</b>",
                title_font=dict(color="#0f172a", size=13),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#f8fafc",
                margin=dict(l=140, r=40, t=40, b=30),
                xaxis=dict(title=dict(text="SHAP Feature Importance Contribution (%)", font=dict(color="#475569")), showgrid=True, gridcolor="#e2e8f0", tickfont=dict(color="#475569")),
                yaxis=dict(tickfont=dict(color="#334155", size=10), showgrid=False),
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.caption("SHAP values (Shapley Additive Explanations) quantify the marginal contribution of each telemetry signal.")
        else:
            st.dataframe(attribution_df, hide_index=True)
