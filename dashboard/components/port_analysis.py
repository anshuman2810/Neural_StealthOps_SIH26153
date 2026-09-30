import streamlit as st
from typing import Dict, Any

def render_port_analysis(port_transition_data: Dict[str, Any]):
    """
    Renders port-to-port state transitions across 7 port states,
    mirroring the network attack stages at the port layer.
    """
    st.markdown("### Port State-Transition Dynamics: Port-to-Port Kill-Chain Progression")
    st.caption(r"Port State Dynamics $P(S_{t+1}^{(port)} \mid S_t^{(port)})$: Tracks real-time attacker port-to-port pivots and forecasts next targeted service daemons.")

    if not port_transition_data:
        st.info("No port transition telemetry available.")
        return

    states = port_transition_data.get("states", [])
    trans = port_transition_data.get("transition_info", {})

    # Top Transition Pipeline Banner
    current_state = trans.get("current_state", "Normal")
    projected_state = trans.get("projected_state", "Normal")
    previous_state = trans.get("previous_state", "Normal")
    trans_prob = trans.get("transition_prob", 85.0)
    reason = trans.get("transition_reason", "Baseline conformance.")
    current_color = trans.get("current_color", "#059669")
    projected_color = trans.get("projected_color", "#2563eb")
    is_attack_active = trans.get("is_attack_active", False)

    status_badge = "ACTIVE PORT TRANSITION DETECTED" if is_attack_active else "BASELINE PORT CONFORMANCE"
    badge_bg = "#fef2f2" if is_attack_active else "#ecfdf5"
    badge_border = "#fca5a5" if is_attack_active else "#6ee7b7"
    badge_text = "#b91c1c" if is_attack_active else "#047857"

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; 
                    padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 10px;">
                <div style="font-size: 0.72rem; font-weight: 800; background: {badge_bg}; color: {badge_text}; 
                            border: 1px solid {badge_border}; padding: 3px 10px; border-radius: 4px; text-transform: uppercase;">
                    {status_badge}
                </div>
                <div style="color: #475569; font-size: 0.80rem; font-weight: 600;">
                    Transition Forecast Certainty: <b style="color: #0f172a;">{trans_prob:.1f}%</b>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin: 10px 0;">
                <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px 14px; text-align: center; flex: 1; min-width: 140px;">
                    <div style="color: #64748b; font-size: 0.68rem; font-weight: 700; text-transform: uppercase;">Previous State (t-10s)</div>
                    <div style="color: #1e293b; font-size: 0.88rem; font-weight: 700; margin-top: 2px;">{previous_state}</div>
                </div>
                <div style="color: #64748b; font-size: 1.1rem; font-weight: 800; padding: 0 6px;">
                    &rarr;
                </div>
                <div style="background: {current_color}14; border: 2px solid {current_color}; border-radius: 6px; padding: 8px 14px; text-align: center; flex: 1.2; min-width: 160px; box-shadow: 0 2px 6px {current_color}33;">
                    <div style="color: {current_color}; font-size: 0.68rem; font-weight: 800; text-transform: uppercase;">Active Port State (t)</div>
                    <div style="color: #0f172a; font-size: 0.95rem; font-weight: 800; margin-top: 2px;">{current_state}</div>
                </div>
                <div style="color: #2563eb; font-size: 1.1rem; font-weight: 800; padding: 0 6px;">
                    &rarr;
                </div>
                <div style="background: #ffffff; border: 2px dashed {projected_color}; border-radius: 6px; padding: 8px 14px; text-align: center; flex: 1.2; min-width: 160px;">
                    <div style="color: {projected_color}; font-size: 0.68rem; font-weight: 800; text-transform: uppercase;">Projected Port State (t+10s)</div>
                    <div style="color: #0f172a; font-size: 0.95rem; font-weight: 800; margin-top: 2px;">{projected_state}</div>
                </div>
            </div>
            <div style="color: #475569; font-size: 0.80rem; margin-top: 10px; line-height: 1.35; border-top: 1px solid #e2e8f0; padding-top: 8px;">
                <b>Transition Dynamics Analysis:</b> {reason}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 7 Port State Cards lined up horizontally (just like the 7 MITRE stages)
    cols = st.columns(len(states))

    for col, st_item in zip(cols, states):
        is_act = st_item["is_active"]
        is_nxt = st_item["is_next"]
        is_prv = st_item["is_prev"]
        theme_c = st_item["theme_color"]
        badge_text_card = st_item["status"]
        share = st_item["share_pct"]
        flows = st_item["flow_count"]

        if is_act:
            border_c = theme_c
            bg_c = f"{theme_c}14"
            title_c = "#0f172a"
            badge_c = theme_c
            shadow_c = f"box-shadow: 0 3px 8px {theme_c}33;"
            border_style = "2px solid"
        elif is_nxt:
            border_c = theme_c
            bg_c = "#ffffff"
            title_c = "#0f172a"
            badge_c = theme_c
            shadow_c = "box-shadow: 0 1px 4px rgba(0,0,0,0.06);"
            border_style = "2px dashed"
        elif is_prv:
            border_c = "#94a3b8"
            bg_c = "#f8fafc"
            title_c = "#334155"
            badge_c = "#64748b"
            shadow_c = "box-shadow: 0 1px 3px rgba(0,0,0,0.04);"
            border_style = "1.5px solid"
        else:
            border_c = "#cbd5e1"
            bg_c = "#ffffff"
            title_c = "#334155"
            badge_c = "#64748b"
            shadow_c = "box-shadow: 0 1px 3px rgba(0,0,0,0.04);"
            border_style = "1.5px solid"

        with col:
            st.markdown(
                f"""
                <div style="background: {bg_c}; border: {border_style} {border_c}; 
                            border-radius: 8px; padding: 10px 8px; min-height: 155px; text-align: center; {shadow_c}">
                    <div style="font-size: 0.68rem; font-weight: 800; color: {badge_c}; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {badge_text_card}
                    </div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {title_c}; margin: 5px 0 2px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{st_item['name']}">
                        {st_item['short_name']}
                    </div>
                    <div style="font-size: 0.70rem; color: #64748b; font-weight: 600;">
                        {st_item['subtitle']}
                    </div>
                    <div style="font-size: 0.66rem; color: #64748b; margin-top: 5px; line-height: 1.25; min-height: 32px;">
                        {st_item['desc']}
                    </div>
                    <div style="margin-top: 6px; border-top: 1px solid #e2e8f0; padding-top: 4px; font-size: 0.68rem; color: #475569; font-weight: 600;">
                        {flows} flows ({share:.1f}%)
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
