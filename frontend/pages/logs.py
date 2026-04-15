from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from components.header import render_header
from components.sidebar import render_sidebar
from components.theme import apply_page_config, get_mock_events


def render_page() -> None:
    apply_page_config("System Logs")
    render_sidebar("logs")
    render_header("logs", "run_logs_header")

    st.markdown("<div class='page-title'>System Events</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Real-time orchestration logs and audit trails for the logistics network.</div>",
        unsafe_allow_html=True,
    )

    controls = st.columns([1.3, 1.1, 1.3, 1.2, 1], gap="medium")
    node_type = controls[0].selectbox(
        "Agent Node Type",
        ["All Dynamic Nodes", "Gateway Nodes", "Vehicle Nodes", "Core System Nodes", "Hub Nodes"],
        key="logs_node_type",
    )
    severity = controls[1].radio("Severity", ["ALL", "INFO", "WARN", "ERROR"], horizontal=True, key="logs_severity")
    date_range = controls[2].date_input(
        "Temporal Range",
        value=(date(2026, 4, 15), date(2026, 4, 15)),
        key="logs_date_range",
    )
    live_feed = controls[3].toggle("Live Feed", value=True, key="logs_live_feed")
    csv_data = pd.DataFrame(get_mock_events()).to_csv(index=False).encode("utf-8")
    controls[4].download_button("Export CSV", data=csv_data, file_name="system_events.csv", mime="text/csv")

    events = pd.DataFrame(get_mock_events())
    node_filters = {
        "Gateway Nodes": ["GW-ALPHA-09"],
        "Vehicle Nodes": ["UAV-FLIGHT-66", "FREIGHT-TRUCK-A1"],
        "Core System Nodes": ["SYS-KERN-AUTH"],
        "Hub Nodes": ["HUB-CHICAGO-04"],
    }
    if node_type in node_filters:
        events = events[events["Agent Node"].isin(node_filters[node_type])]
    if severity != "ALL":
        key = {"INFO": "OK", "WARN": "WRN", "ERROR": "ERR"}[severity]
        events = events[events["Status"].str.contains(key)]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        event_dates = pd.to_datetime(events["Timestamp"]).dt.date
        events = events[(event_dates >= start) & (event_dates <= end)]

    st.dataframe(events, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(events)} of 12,844 entries")
    if live_feed:
        st.success("Live feed is active. New events will stream into the table automatically.")


render_page()
