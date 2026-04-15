from __future__ import annotations

import streamlit as st

from components.header import render_header
from components.sidebar import render_sidebar
from components.theme import apply_page_config, metric_card


AGENTS = {
    "Demand Prediction": {
        "uptime": "14d 02h 11m",
        "confidence": "98.2%",
        "status": "OPTIMAL",
        "throughput": "1,240 msg/s",
        "memory": "3.2 GB",
        "error_rate": "0.002%",
        "last_sync": "24s ago",
    },
    "Store Allocation": {
        "uptime": "0d 00h 45m",
        "confidence": "94.1%",
        "status": "IDLE",
        "throughput": "920 msg/s",
        "memory": "2.4 GB",
        "error_rate": "0.010%",
        "last_sync": "46s ago",
    },
    "Route Optimizer": {
        "uptime": "4d 19h 22m",
        "confidence": "91.4%",
        "status": "LATENCY",
        "throughput": "880 msg/s",
        "memory": "4.1 GB",
        "error_rate": "0.041%",
        "last_sync": "1m ago",
    },
    "Fleet Dispatch": {
        "uptime": "32d 11h 05m",
        "confidence": "99.1%",
        "status": "ACTIVE",
        "throughput": "1,870 msg/s",
        "memory": "2.9 GB",
        "error_rate": "0.001%",
        "last_sync": "11s ago",
    },
}


def render_page() -> None:
    apply_page_config("Agent Fleet")
    render_sidebar("agents")
    render_header("agents", "run_agents_header")

    st.markdown("<div class='page-title'>Agent Fleet Management</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Orchestrating 12 active AI agents across 4 global nodes.</div>", unsafe_allow_html=True)

    top = st.columns([1, 1, 1, 1.2], gap="medium")
    top[0].markdown(metric_card("Fleet Health", "99.98%", "+0.02%"), unsafe_allow_html=True)
    top[1].markdown(metric_card("Active Queries", "12.4k", "per min"), unsafe_allow_html=True)
    top[2].markdown(metric_card("Compute Load", "42%", "balanced"), unsafe_allow_html=True)
    top[3].markdown(
        "<div class='metric-card'><div class='metric-label'>Live Network Map</div><div style='height:128px;border-radius:16px;background:rgba(184,227,233,.5);display:flex;align-items:center;justify-content:center;color:#0B2E33;font-weight:800;'>300 x 300</div><div class='metric-helper'>All nodes operational across 3 regions</div></div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1.6], gap="medium")
    with left:
        st.markdown("<div class='section-title'>Agent Registry</div>", unsafe_allow_html=True)
        for name, details in AGENTS.items():
            if st.button(name, key=f"agent_{name}", use_container_width=True):
                st.session_state.selected_agent = name
            st.caption(f"Uptime {details['uptime']} | Confidence {details['confidence']} | {details['status']}")

        st.button("New Shipment", use_container_width=True, key="agents_new_shipment")

    selected = AGENTS[st.session_state.selected_agent]
    with right:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown(f"## {st.session_state.selected_agent} Agent")
        detail_cols = st.columns(4)
        detail_cols[0].metric("Throughput", selected["throughput"])
        detail_cols[1].metric("Memory Use", selected["memory"])
        detail_cols[2].metric("Error Rate", selected["error_rate"])
        detail_cols[3].metric("Last Sync", selected["last_sync"])
        st.markdown("#### Live Activity Feed")
        st.code(
            "\n".join(
                [
                    "[INFO] Model inference completed. Confidence 0.982. Updating local cache.",
                    "[SYNC] Pushing idle update to US-EAST-01 distribution point.",
                    "[INFO] Store allocation request received from Store-1849.",
                    "[WARN] Node US-WEST-82 reporting slight packet loss. Re-routing via secondary path.",
                    "[INFO] Heartbeat signal acknowledged by orchestration controller.",
                ]
            ),
            language="text",
        )
        toggles = st.columns(2)
        self_healing = toggles[0].toggle("Self-Healing", value=True)
        burst_capacity = toggles[1].toggle("Burst Capacity", value=False)
        action_cols = st.columns([1, 1, 1.2])
        if action_cols[1].button("Suspend Agent", use_container_width=True):
            st.warning(f"{st.session_state.selected_agent} has been suspended.")
        if action_cols[2].button("Save Changes", use_container_width=True):
            st.success(
                f"Configuration saved for {st.session_state.selected_agent}. Self-Healing={'ON' if self_healing else 'OFF'}, Burst Capacity={'ON' if burst_capacity else 'OFF'}."
            )
        st.markdown("</div>", unsafe_allow_html=True)


render_page()
