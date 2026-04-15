from __future__ import annotations

import pandas as pd
import streamlit as st

from components.header import render_header
from components.sidebar import render_sidebar
from components.theme import apply_page_config


def render_page() -> None:
    apply_page_config("Analytics")
    render_sidebar("analytics")
    render_header("analytics", "run_analytics_header")

    st.markdown("<div class='page-title'>Analytics</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Trend monitoring across demand, inventory usage, transfers, and agent health.</div>",
        unsafe_allow_html=True,
    )

    demand_trend = pd.DataFrame(
        {
            "hour": list(range(8, 20)),
            "demand": [42, 48, 51, 58, 72, 81, 88, 94, 79, 68, 61, 52],
        }
    ).set_index("hour")
    inventory_usage = pd.DataFrame(
        {"group": ["Produce", "Dairy", "Snacks", "Beverages"], "usage": [84, 66, 55, 73]}
    ).set_index("group")
    transfer_timeline = pd.DataFrame(
        {"window": ["08:00", "10:00", "12:00", "14:00", "16:00"], "transfers": [12, 18, 24, 21, 15]}
    ).set_index("window")
    donut = pd.DataFrame({"segment": ["Healthy", "Warning", "Critical"], "value": [82, 12, 6]})

    row_one = st.columns(2, gap="medium")
    with row_one[0]:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Demand Trend")
        st.line_chart(demand_trend)
        st.markdown("</div>", unsafe_allow_html=True)
    with row_one[1]:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Inventory Usage")
        st.bar_chart(inventory_usage)
        st.markdown("</div>", unsafe_allow_html=True)

    row_two = st.columns(2, gap="medium")
    with row_two[0]:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Transfer Activity Timeline")
        st.area_chart(transfer_timeline)
        st.markdown("</div>", unsafe_allow_html=True)
    with row_two[1]:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Agent Health Distribution")
        st.vega_lite_chart(
            donut,
            {
                "mark": {"type": "arc", "innerRadius": 55},
                "encoding": {
                    "theta": {"field": "value", "type": "quantitative"},
                    "color": {
                        "field": "segment",
                        "type": "nominal",
                        "scale": {"range": ["#16A34A", "#F97316", "#DC2626"]},
                    },
                    "tooltip": [{"field": "segment"}, {"field": "value"}],
                },
            },
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


render_page()
