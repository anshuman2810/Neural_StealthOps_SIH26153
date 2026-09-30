from pathlib import Path
import streamlit as st

def render_landing_page():
    """
    Renders the executive Landing Page with a two-column layout:
    - Left Column: Welcome message, SIH-26153 details, DIAT branding, and diat-logo.png
    - Right Column: 'Select an option to proceed' and two horizontally placed tactical cards
      for launching either the Infiltration Prediction Engine or System Health & Management Dashboard.
    """
    root_dir = Path(__file__).resolve().parent.parent.parent
    logo_path = root_dir / "diat-logo.png"

    # Custom styling for landing page elements
    st.markdown(
        """
        <style>
        .landing-header-badge {
            display: inline-block;
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
            color: #ffffff;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 20px;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
        }
        .landing-left-container {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1.5px solid #cbd5e1;
            border-radius: 12px;
            padding: 32px 28px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .welcome-title {
            font-size: 2.1rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.25;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }
        .welcome-sub {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2563eb;
            margin-bottom: 12px;
            line-height: 1.4;
        }
        .welcome-inst {
            font-size: 1.05rem;
            font-weight: 700;
            color: #334155;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .landing-right-container {
            background: #ffffff;
            border: 1.5px solid #cbd5e1;
            border-radius: 12px;
            padding: 32px 28px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
            height: 100%;
        }
        .selection-prompt {
            font-size: 1.35rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }
        .tactical-card-box {
            background: #f8fafc;
            border: 1.5px solid #cbd5e1;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.2s ease-in-out;
            min-height: 290px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .tactical-card-box:hover {
            border-color: #2563eb;
            box-shadow: 0 6px 18px rgba(37, 99, 235, 0.12);
            background: #ffffff;
            transform: translateY(-2px);
        }
        .card-icon {
            font-size: 2.2rem;
            margin-bottom: 10px;
        }
        .card-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 8px;
            line-height: 1.3;
        }
        .card-desc {
            font-size: 0.88rem;
            color: #475569;
            line-height: 1.45;
            margin-bottom: 14px;
            flex-grow: 1;
        }
        .card-tag {
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            margin-bottom: 14px;
            width: fit-content;
        }
        .tag-active {
            background: rgba(34, 197, 94, 0.15);
            color: #15803d;
            border: 1px solid #86efac;
        }
        .tag-telemetry {
            background: rgba(14, 165, 233, 0.15);
            color: #0369a1;
            border: 1px solid #7dd3fc;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Main split layout: 50% Left / 50% Right
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="landing-header-badge">Smart India Hackathon 2026</div>
            <div class="welcome-title">Welcome to team NeuralOps</div>
            <div class="welcome-sub">SIH-26153: AI based Network Attack Forecasting from Network Traffic Data</div>
            <div class="welcome-inst">
                <span>🏛️</span> Defence Institute of Advanced Technology (DIAT)
            </div>
            """,
            unsafe_allow_html=True
        )

        if logo_path.exists():
            st.image(str(logo_path), caption="Defence Institute of Advanced Technology, Pune", use_container_width=True)
        else:
            st.info("Defence Institute of Advanced Technology (DIAT)")

        st.markdown(
            """
            <div style="margin-top: 20px; padding: 14px; background: #f1f5f9; border-radius: 8px; border-left: 4px solid #2563eb; font-size: 0.85rem; color: #334155;">
                <strong>System Overview:</strong> Proactive intrusion detection powered by temporal AI World Models. Real-time discrete 10-second telemetry state encoding, multi-step kill-chain hazard anticipation (+10s, +30s, +60s), and continuous infrastructure telemetry.
            </div>
            """,
            unsafe_allow_html=True
        )

    with right_col:
        st.markdown(
            """
            <div class="selection-prompt">
                🚀 Select an option to proceed
            </div>
            <p style="color: #64748b; font-size: 0.92rem; margin-top: -12px; margin-bottom: 24px;">
                Choose an operational environment below to launch live threat simulation or access cluster telemetry.
            </p>
            """,
            unsafe_allow_html=True
        )

        # Horizontally placed tactical cards
        card_col1, card_col2 = st.columns(2, gap="medium")

        with card_col1:
            st.markdown(
                """
                <div class="tactical-card-box">
                    <div>
                        <div class="card-icon">🧠</div>
                        <span class="card-tag tag-active">● Active Inference</span>
                        <div class="card-title">Infiltration Prediction Engine Dashboard</div>
                        <div class="card-desc">
                            Real-time AI SOC Console for multi-horizon attack forecasting (+10s, +30s, +60s), MITRE ATT&CK progression tracking, 6-step autoregressive rollouts, port dynamics, and SHAP explainability.
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("Launch Threat Engine →", key="btn_launch_threat_engine", use_container_width=True):
                st.session_state.current_page = "threat_engine"
                st.rerun()

        with card_col2:
            st.markdown(
                """
                <div class="tactical-card-box">
                    <div>
                        <div class="card-icon">🖥️</div>
                        <span class="card-tag tag-telemetry">● Infrastructure Telemetry</span>
                        <div class="card-title">System Health & Management Dashboard</div>
                        <div class="card-desc">
                            Telemetry control plane monitoring Data Lakehouse (Iceberg & Ceph), Packet Processing Pipeline compute nodes, Redis shared cache, live blinking LEDs, resource gauges, and node configurations.
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("Launch System Console →", key="btn_launch_system_mgmt", use_container_width=True):
                st.session_state.current_page = "system_management"
                st.rerun()

        # Quick summary stats footer
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 8px; padding: 14px 18px; display: flex; justify-content: space-around; text-align: center;">
                <div>
                    <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Prediction Horizon</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #2563eb;">+10s / +30s / +60s</div>
                </div>
                <div style="border-right: 1px solid #e2e8f0;"></div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Inference Latency</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #16a34a;">0.19 ms (CPU)</div>
                </div>
                <div style="border-right: 1px solid #e2e8f0;"></div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Cluster Status</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #16a34a;">HEALTH_OK (All Nodes)</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
