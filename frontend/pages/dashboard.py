from __future__ import annotations

from typing import Any, Dict

import requests
import streamlit as st

from components.header import render_header
from components.sidebar import render_sidebar
from components.theme import apply_page_config, badge_html, set_global_status, status_kind


STORE_DATA = {
    "Store A": {"inventory": 820, "load": 54, "distance": 4},
    "Store B": {"inventory": 640, "load": 72, "distance": 8},
    "Store C": {"inventory": 320, "load": 91, "distance": 12},
}


def api_post(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{st.session_state.backend_url}{endpoint}", json=payload, timeout=12)
    response.raise_for_status()
    return response.json()


def weather_to_rainfall(weather: str) -> int:
    return {"Sunny": 10, "Rain": 65, "Storm": 100}.get(weather, 20)


def build_recommended_actions() -> list[str]:
    outputs = st.session_state.dashboard_outputs
    actions: list[str] = []
    allocation = outputs.get("allocation")
    if allocation:
        actions.append(f"Redirect high-priority orders to {allocation['store']}.")
    inventory = outputs.get("inventory")
    if inventory and inventory["transfer"]:
        if inventory["direction"] == "A -> B":
            actions.append(f"Transfer {inventory['transfer']} units from Store A to Store B.")
        elif inventory["direction"] == "B -> A":
            actions.append(f"Transfer {inventory['transfer']} units from Store B to Store A.")
    layout = outputs.get("layout")
    if layout:
        actions.append(f"Prioritize front-facing slots and move fast movers toward {layout['position']}.")
    capacity = outputs.get("capacity")
    if capacity and capacity["status"] == "Activated":
        actions.append("Activate the ghost store buffer and shift overflow demand.")
    error = outputs.get("error")
    if error and error["status"] == "Manifest Match":
        actions.append("Maintain scan verification at the current checkpoint to prevent pick errors.")
    if not actions:
        actions = [
            "Redirect high-priority orders to Store B.",
            "Transfer 33 units from Store A to Store B.",
            "Prioritize front-facing slots for Milk, Bread.",
            "Activate the ghost store buffer and shift overflow demand.",
            "Maintain scan verification at the current checkpoint to prevent pick errors.",
        ]
    return actions


def render_alert_and_hero() -> None:
    outputs = st.session_state.dashboard_outputs
    demand = outputs.get("demand", {"level": "HIGH", "confidence": 92, "recommendation": "Immediate load balancing recommended"})
    capacity = outputs.get("capacity", {"status": "Activated"})
    critical = demand["level"] == "HIGH" or capacity.get("status") == "Activated"
    title = "DEMAND SURGE DETECTED" if critical else "NETWORK STABLE"
    message = (
        "Immediate action required. Capacity and store routing should be reviewed now."
        if critical
        else "Demand and capacity are within expected operating thresholds."
    )
    system_health = 94.9 if critical else 99.2
    system_status = "High Load" if critical else "Optimal"

    st.markdown(
        f"<div class='alert-strip'><div class='alert-strip-title'>{title}</div><div class='alert-strip-copy'>{message}</div></div>",
        unsafe_allow_html=True,
    )
    hero_cols = st.columns([1.4, 1], gap="medium")
    hero_cols[0].markdown(
        (
            "<div class='hero-panel info'>"
            "<div class='hero-title'>Demand Risk</div>"
            f"<div class='hero-value'>{demand['level']}</div>"
            f"<div class='hero-copy'><strong>Demand score:</strong> {demand['confidence']} / 100</div>"
            f"<div class='hero-copy'>{demand['recommendation']}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    hero_cols[1].markdown(
        (
            "<div class='hero-panel info'>"
            "<div class='hero-title'>System Health</div>"
            f"<div class='hero-value'>{system_health}%</div>"
            f"<div class='hero-copy'><strong>Status:</strong> {system_status}</div>"
            "<div class='hero-copy'>Watch capacity and picking exceptions</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_recommended_actions() -> None:
    items = "".join(f"<li>{action}</li>" for action in build_recommended_actions())
    st.markdown(
        f"<div class='recommendation-panel'><div class='recommendation-title'>Recommended Actions</div><ul>{items}</ul></div>",
        unsafe_allow_html=True,
    )


def render_page() -> None:
    apply_page_config("MALO Dashboard")
    render_sidebar("overview")
    run_clicked = render_header("dashboard", "header_run_dashboard")

    st.markdown("<div class='page-kicker'>Global Operations Center</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-title'>Operations Dashboard</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Live orchestration across demand prediction, inventory balancing, shelf optimization, and manifest validation.</div>",
        unsafe_allow_html=True,
    )
    render_alert_and_hero()

    if run_clicked:
        with st.spinner("Running full simulation across all agents..."):
            st.success("Simulation completed. Agent cards updated with the latest outputs.")

    top_row = st.columns(3, gap="medium")
    bottom_row = st.columns(3, gap="medium")

    with top_row[0]:
        with st.container(border=False):
            st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
            st.markdown("#### Demand Prediction")
            weather = st.selectbox("Weather forecast", ["Sunny", "Rain", "Storm"], key="weather_dashboard")
            festival = st.checkbox("Festival Multiplier Active", key="festival_dashboard")
            social_trend = st.slider("Social Sentiment Trend", 0, 100, 60, key="social_dashboard")
            if st.button("Predict Demand", use_container_width=True, key="predict_demand_btn"):
                with st.spinner("Evaluating demand signals..."):
                    result = api_post("/predict-demand", {"rainfall": weather_to_rainfall(weather), "festival": festival})
                    demand_level = result["demand_level"]
                    confidence = min(98, 58 + social_trend // 2 + (12 if festival else 0))
                    recommendation = {
                        "HIGH": "Monsoon approach triggering increased demand for perishables.",
                        "MEDIUM": "Demand is rising. Review fast-moving inventory positions.",
                        "LOW": "Demand stable. Continue normal fulfillment planning.",
                    }[demand_level]
                    st.session_state.dashboard_outputs["demand"] = {
                        "level": demand_level,
                        "confidence": confidence,
                        "recommendation": recommendation,
                    }
                    set_global_status("ACTIVE" if demand_level != "HIGH" else "ACTIVE", st.session_state.global_metrics["scenario"], 6)
            output = st.session_state.dashboard_outputs.get("demand", {"level": "MEDIUM", "confidence": 88, "recommendation": "Monsoon approaching."})
            st.markdown(
                f"{badge_html(output['level'], status_kind(output['level']))}<div style='height:0.6rem'></div>"
                f"<strong>{output['confidence']}%</strong> confidence<br><span style='color:rgba(11,46,51,0.68)'>{output['recommendation']}</span>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

    with top_row[1]:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Store Allocation")
        order_id = st.text_input("Active order ID", value="ORD-7729-LX", key="order_id_dashboard")
        selected_store = st.radio("Available stores", list(STORE_DATA.keys()), key="store_radio_dashboard")
        for name, details in STORE_DATA.items():
            st.caption(f"{name}: Inventory {details['inventory']} | Load {details['load']}% | Distance {details['distance']} km")
        if st.button("Assign Node", use_container_width=True, key="assign_node_btn"):
            with st.spinner("Assigning optimal node..."):
                payload = {
                    "store_load": [{"store": store, "load": details["load"]} for store, details in STORE_DATA.items()],
                    "distance": {store: details["distance"] for store, details in STORE_DATA.items()},
                    "inventory": {store: details["inventory"] for store, details in STORE_DATA.items()},
                }
                result = api_post("/allocate-store", payload)
                store = result["result"]["selected_store"]
                selected = STORE_DATA.get(store, STORE_DATA["Store A"])
                status = "Optimal" if selected["load"] < 70 else "Stress" if selected["load"] < 90 else "Capacity"
                st.session_state.dashboard_outputs["allocation"] = {
                    "store": store,
                    "eta": f"{selected['distance'] + 8} min",
                    "status": status,
                }
        output = st.session_state.dashboard_outputs.get("allocation", {"store": "Store A", "eta": "12 min", "status": "Optimal"})
        st.markdown(
            f"{badge_html(output['status'], status_kind(output['status']))}<div style='height:0.6rem'></div>"
            f"<strong>{output['store']}</strong> assigned<br><span style='color:rgba(11,46,51,0.68)'>ETA {output['eta']}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with top_row[2]:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Inventory Balancing")
        stock_a = st.number_input("Store A stock", min_value=0, value=1250, key="balance_stock_a")
        stock_b = st.number_input("Store B stock", min_value=0, value=450, key="balance_stock_b")
        threshold = st.number_input("Safety threshold", min_value=0, value=600, key="balance_threshold")
        if st.button("Balance Stocks", use_container_width=True, key="balance_stocks_btn"):
            with st.spinner("Calculating transfer requirement..."):
                result = api_post("/balance-inventory", {"stock_levels": {"Store A": stock_a, "Store B": stock_b}})
                actions = result["result"]["actions"]
                if actions and abs(stock_a - stock_b) >= threshold:
                    action = actions[0]
                    st.session_state.dashboard_outputs["inventory"] = {
                        "transfer": action["units"],
                        "direction": f"{action['from_store'][-1]} -> {action['to_store'][-1]}",
                    }
                else:
                    st.session_state.dashboard_outputs["inventory"] = {"transfer": 0, "direction": "Balanced"}
        output = st.session_state.dashboard_outputs.get("inventory", {"transfer": 200, "direction": "B -> A"})
        st.markdown(
            f"<div style='font-size:2rem;font-weight:800;color:#0B2E33'>{output['transfer']}</div>"
            f"<div style='color:rgba(11,46,51,0.68)'>Units transfer | {output['direction']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_row[0]:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Shelf Optimization")
        product_group = st.selectbox("Product Group", ["Organic Produce", "Dairy", "Beverages"], key="product_group_dashboard")
        pick_frequency = st.number_input("Pick Frequency", min_value=0, value=128, key="pick_frequency_dashboard")
        current_position = st.text_input("Current Position", value="C-09", key="current_position_dashboard")
        if st.button("Run Optimizer", use_container_width=True, key="run_optimizer_btn"):
            with st.spinner("Optimizing shelf placement..."):
                result = api_post(
                    "/optimize-layout",
                    {"picking_frequency": {product_group: pick_frequency, "Snacks": 72, "Bakery": 48}},
                )
                new_position = result["result"]["new_shelf_positions"][0]["new_position"]
                efficiency_gain = min(32, 10 + pick_frequency // 8)
                st.session_state.dashboard_outputs["layout"] = {
                    "position": new_position.replace("Shelf", "").strip() or "B-12",
                    "gain": efficiency_gain,
                }
        output = st.session_state.dashboard_outputs.get("layout", {"position": "B-12", "gain": 18})
        st.markdown(
            f"<strong>Recommendation:</strong> Move to {output['position']}<br><span style='color:rgba(11,46,51,0.68)'>+{output['gain']}% efficiency</span>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_row[1]:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Ghost Activation")
        backlog_orders = st.number_input("Backlog Orders", min_value=0, value=42, key="backlog_orders_dashboard")
        capacity_cap = st.number_input("Capacity Cap", min_value=0, value=500, key="capacity_cap_dashboard")
        if st.button("Status Check", use_container_width=True, key="status_check_btn"):
            with st.spinner("Checking overflow capacity..."):
                result = api_post("/activate-capacity", {"demand": backlog_orders, "capacity": capacity_cap})
                activated = result["result"]["activate_ghost_store"]
                st.session_state.dashboard_outputs["capacity"] = {
                    "status": "Activated" if activated else "Not Activated",
                    "coverage": result["result"]["reason"],
                }
        output = st.session_state.dashboard_outputs.get("capacity", {"status": "Not Activated", "coverage": "Current capacity can absorb the backlog."})
        st.markdown(
            f"{badge_html(output['status'], status_kind(output['status']))}<div style='height:0.6rem'></div>"
            f"<span style='color:rgba(11,46,51,0.68)'>{output['coverage']}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_row[2]:
        st.markdown("<div class='card-shell'>", unsafe_allow_html=True)
        st.markdown("#### Error Detection")
        expected_manifest = st.text_input("Expected Manifest", value="SHA-256: 7B-92-A1", key="expected_manifest_dashboard")
        scanned_manifest = st.text_input("Scanned Manifest", value="SHA-256: 7B-92-A1", key="scanned_manifest_dashboard")
        if st.button("Validate Integrity", use_container_width=True, key="validate_integrity_btn"):
            with st.spinner("Validating manifest integrity..."):
                result = api_post("/check-error", {"expected_item": expected_manifest, "scanned_item": scanned_manifest})
                ok = result["result"]["status"] == "success"
                st.session_state.dashboard_outputs["error"] = {
                    "status": "Manifest Match" if ok else "Mismatch Alert",
                    "message": result["result"]["message"],
                }
        output = st.session_state.dashboard_outputs.get("error", {"status": "Manifest Match", "message": "No mismatch detected."})
        st.markdown(
            f"{badge_html(output['status'], status_kind(output['status']))}<div style='height:0.6rem'></div>"
            f"<span style='color:rgba(11,46,51,0.68)'>{output['message']}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>System Orchestration Logs</div>", unsafe_allow_html=True)
    logs = [
        {"Timestamp": "2026-04-15 14:21:44", "Agent Node": "Node 02", "Event Description": "Autonomous allocation assigned ORD-7729 to Store A. ETA optimized to 12m.", "Status": "PEAK-OK"},
        {"Timestamp": "2026-04-15 14:18:09", "Agent Node": "Node 01", "Event Description": "Demand prediction updated based on NOAA weather feed [Monsoon-24-A].", "Status": "DATA-UP"},
        {"Timestamp": "2026-04-15 14:15:50", "Agent Node": "Node 06", "Event Description": "Integrity validation for Manifest B-91-X completed. No drift detected.", "Status": "SAFE-JOB"},
        {"Timestamp": "2026-04-15 14:12:31", "Agent Node": "Node 03", "Event Description": "Rebalancing request generated for Store B due to threshold breach.", "Status": "WARN-THR"},
        {"Timestamp": "2026-04-15 14:09:10", "Agent Node": "Node 04", "Event Description": "Shelf optimizer triggered for Organic Produce at Slot C-09. Recommended B-12.", "Status": "EXEC-LOG"},
    ]
    st.dataframe(logs, use_container_width=True, hide_index=True)
    render_recommended_actions()


if __name__ == "__main__":
    render_page()
