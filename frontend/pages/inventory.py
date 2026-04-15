from __future__ import annotations

import pandas as pd
import streamlit as st

from components.header import render_header
from components.sidebar import render_sidebar
from components.theme import apply_page_config, metric_card


def render_page() -> None:
    apply_page_config("Inventory Hub")
    render_sidebar("inventory")
    render_header("inventory", "run_inventory_header")

    st.markdown("<div class='page-kicker'>Global Network Status</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-title'>Inventory Hub</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Real-time micro-fulfillment availability, transfer coordination, and shortage tracking.</div>",
        unsafe_allow_html=True,
    )

    metrics = st.columns(3)
    metrics[0].markdown(metric_card("Active SKUs", "42,891", "Across the network"), unsafe_allow_html=True)
    metrics[1].markdown(metric_card("Network Capacity", "84.2%", "Current available throughput"), unsafe_allow_html=True)
    metrics[2].markdown(metric_card("Critical Alerts", "12", "Action required"), unsafe_allow_html=True)

    left, right = st.columns([2.3, 1], gap="medium")
    with left:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Stock Density Heatmap")
        st.caption("Real-time micro-fulfillment center availability")
        st.markdown(
            """
            <div style="position:relative;height:520px;border-radius:24px;background:
            radial-gradient(circle at 55% 35%, rgba(22,163,74,.28), transparent 10%),
            radial-gradient(circle at 68% 58%, rgba(249,115,22,.24), transparent 12%),
            radial-gradient(circle at 45% 52%, rgba(37,99,235,.22), transparent 9%),
            linear-gradient(135deg, rgba(11,46,51,.85), rgba(79,124,130,.55));overflow:hidden;">
                <div style="position:absolute;inset:0;background-image:
                radial-gradient(rgba(255,255,255,.10) 1px, transparent 1px);
                background-size: 10px 10px;opacity:.35;"></div>
                <div style="position:absolute;left:42%;top:30%;width:18px;height:18px;border-radius:50%;border:3px solid #ffffff;background:#16A34A;"></div>
                <div style="position:absolute;left:60%;top:52%;width:18px;height:18px;border-radius:50%;border:3px solid #ffffff;background:#F97316;"></div>
                <div style="position:absolute;left:48%;top:48%;width:12px;height:12px;border-radius:50%;border:3px solid #ffffff;background:#2563EB;"></div>
                <div style="position:absolute;left:10%;bottom:12%;background:#ffffff;border-radius:18px;padding:1rem 1.1rem;width:230px;box-shadow:0 8px 24px rgba(11,46,51,.15);">
                    <div style="font-size:.72rem;color:rgba(11,46,51,.6);font-weight:700;letter-spacing:.08em;text-transform:uppercase;">Selected Location</div>
                    <div style="font-size:1.2rem;color:#0B2E33;font-weight:800;margin-top:.4rem;">MFC-72: Downtown Loop</div>
                    <div style="display:flex;gap:1.2rem;margin-top:1rem;color:#0B2E33;">
                        <div><div style="font-size:.72rem;color:rgba(11,46,51,.55)">Load</div><div style="font-weight:800;">92% Capacity</div></div>
                        <div><div style="font-size:.72rem;color:rgba(11,46,51,.55)">Robots</div><div style="font-weight:800;">24 Active</div></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Low Stock Alerts")
        shortages = [
            ("Precision Sensor Gen.4", "8 units left (MFC-12)"),
            ("LTE Hub Module", "14 units left (MFC-04)"),
            ("Nexus Phone Ultra", "42 units left (MFC-72)"),
        ]
        for name, detail in shortages:
            st.markdown(f"**{name}**  \n<span style='color:rgba(11,46,51,.65)'>{detail}</span>", unsafe_allow_html=True)
            st.divider()
        st.button("View All Shortages", use_container_width=True, key="view_shortages")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card-shell' style='margin-top:1rem'>", unsafe_allow_html=True)
        st.markdown("#### Transfer Pipeline")
        st.progress(72, text="TR-4492 | MFC-01 -> MFC-12")
        st.progress(18, text="TR-4501 | PORT-A -> MFC-04")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Pending Inventory Transfers</div>", unsafe_allow_html=True)
    action_cols = st.columns([1, 1, 4])
    if action_cols[0].button("New Shipment", use_container_width=True):
        st.success("Shipment request created for inbound inventory.")
    if action_cols[1].button("Initiate Transfer", use_container_width=True):
        st.session_state.inventory_transfers.append(
            {
                "Manifest ID": "MNF-9019-K",
                "Source": "Port-A",
                "Destination": "MFC-04",
                "Quantity": "620 Units",
                "ETA": "Today, 18:20",
                "Status": "QUEUED",
            }
        )
        st.success("Transfer added to pipeline.")

    st.dataframe(pd.DataFrame(st.session_state.inventory_transfers), use_container_width=True, hide_index=True)


render_page()
