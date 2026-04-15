from __future__ import annotations

import streamlit as st


def render_sidebar(active_page: str) -> None:
    """Render the persistent operator sidebar with navigation and quick utilities."""
    with st.sidebar:
        st.markdown("### Global Ops")
        st.caption("Precision Logistics")

        st.page_link("app.py", label="Overview")
        st.page_link("pages/agents.py", label="Agent Fleet")
        st.page_link("pages/inventory.py", label="Inventory Hub")
        st.page_link("pages/logs.py", label="System Logs")
        st.page_link("pages/analytics.py", label="Analytics")

        st.divider()
        st.caption("Current scenario")
        st.write(st.session_state.global_metrics["scenario"])
        st.caption("Active agents")
        st.write(st.session_state.global_metrics["active_agents"])
        st.caption("System status")
        st.write(st.session_state.global_metrics["system_status"])

        st.divider()
        if st.button("Support", use_container_width=True, key=f"support_{active_page}"):
            st.session_state.support_message = "Support ticket panel opened for operations review."
        if st.button("Account", use_container_width=True, key=f"account_{active_page}"):
            st.session_state.account_message = "Operator account settings loaded."

        if st.session_state.support_message:
            st.info(st.session_state.support_message)
        if st.session_state.account_message:
            st.info(st.session_state.account_message)
