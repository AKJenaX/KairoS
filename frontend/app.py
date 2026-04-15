from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Any, Dict, List

import requests
import streamlit as st


st.set_page_config(page_title="MALO Dashboard", layout="wide")


SCENARIO_PRESETS = {
    "Normal Day": {
        "rainfall": 20,
        "festival": False,
        "store_loads": {"Store A": 45.0, "Store B": 35.0, "Store C": 30.0},
        "distances": {"Store A": 2.0, "Store B": 4.0, "Store C": 6.0},
        "allocation_inventory": {"Store A": 60, "Store B": 80, "Store C": 70},
        "balance_inventory": {"Store A": 70, "Store B": 60, "Store C": 55},
        "picking_frequency": {"Milk": 36, "Bread": 30, "Chips": 18, "Juice": 16},
        "demand_units": 90,
        "capacity_units": 120,
        "expected_item": "Organic Milk",
        "scanned_item": "Organic Milk",
    },
    "Heavy Rain + Festival": {
        "rainfall": 95,
        "festival": True,
        "store_loads": {"Store A": 82.0, "Store B": 68.0, "Store C": 58.0},
        "distances": {"Store A": 2.5, "Store B": 4.0, "Store C": 5.5},
        "allocation_inventory": {"Store A": 35, "Store B": 92, "Store C": 55},
        "balance_inventory": {"Store A": 95, "Store B": 28, "Store C": 44},
        "picking_frequency": {"Milk": 58, "Bread": 52, "Chips": 35, "Juice": 28},
        "demand_units": 160,
        "capacity_units": 115,
        "expected_item": "Organic Milk",
        "scanned_item": "Organic Milk",
    },
    "Black Friday Surge": {
        "rainfall": 55,
        "festival": True,
        "store_loads": {"Store A": 90.0, "Store B": 78.0, "Store C": 72.0},
        "distances": {"Store A": 2.0, "Store B": 3.5, "Store C": 5.0},
        "allocation_inventory": {"Store A": 42, "Store B": 105, "Store C": 88},
        "balance_inventory": {"Store A": 120, "Store B": 32, "Store C": 60},
        "picking_frequency": {"Milk": 72, "Bread": 64, "Chips": 48, "Juice": 38},
        "demand_units": 220,
        "capacity_units": 140,
        "expected_item": "Organic Milk",
        "scanned_item": "Almond Milk",
    },
}


def init_state() -> None:
    defaults = SCENARIO_PRESETS["Normal Day"]
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = "Normal Day"
    if "backend_url" not in st.session_state:
        st.session_state.backend_url = "http://127.0.0.1:8000"
    if "simulation_results" not in st.session_state:
        st.session_state.simulation_results = {}
    if "workflow_steps" not in st.session_state:
        st.session_state.workflow_steps = []
    if "last_simulation_error" not in st.session_state:
        st.session_state.last_simulation_error = ""
    if "metrics" not in st.session_state:
        st.session_state.metrics = {"demand_score": 35, "load_reduction": 0.0, "picking_efficiency": 91.0, "system_health": 99.7}
    if "summary" not in st.session_state:
        st.session_state.summary = {"system_status": "Stable", "active_agents": 0, "current_demand_level": "LOW"}
    for field, value in defaults.items():
        if field not in st.session_state:
            st.session_state[field] = value
    sync_widget_state()


def sync_widget_state() -> None:
    st.session_state.rainfall_input = st.session_state.rainfall
    st.session_state.load_a = st.session_state.store_loads["Store A"]
    st.session_state.load_b = st.session_state.store_loads["Store B"]
    st.session_state.load_c = st.session_state.store_loads["Store C"]
    st.session_state.dist_a = st.session_state.distances["Store A"]
    st.session_state.dist_b = st.session_state.distances["Store B"]
    st.session_state.dist_c = st.session_state.distances["Store C"]
    st.session_state.alloc_inv_a = st.session_state.allocation_inventory["Store A"]
    st.session_state.alloc_inv_b = st.session_state.allocation_inventory["Store B"]
    st.session_state.alloc_inv_c = st.session_state.allocation_inventory["Store C"]
    st.session_state.balance_a = st.session_state.balance_inventory["Store A"]
    st.session_state.balance_b = st.session_state.balance_inventory["Store B"]
    st.session_state.balance_c = st.session_state.balance_inventory["Store C"]
    st.session_state.picks_milk = st.session_state.picking_frequency["Milk"]
    st.session_state.picks_bread = st.session_state.picking_frequency["Bread"]
    st.session_state.picks_chips = st.session_state.picking_frequency["Chips"]
    st.session_state.picks_juice = st.session_state.picking_frequency["Juice"]
    st.session_state.demand_units_input = st.session_state.demand_units
    st.session_state.capacity_units_input = st.session_state.capacity_units
    st.session_state.expected_item_input = st.session_state.expected_item
    st.session_state.scanned_item_input = st.session_state.scanned_item


def apply_selected_scenario() -> None:
    preset = SCENARIO_PRESETS[st.session_state.selected_scenario]
    for field, value in preset.items():
        st.session_state[field] = value
    sync_widget_state()


def sync_from_widgets() -> None:
    st.session_state.rainfall = st.session_state.rainfall_input
    st.session_state.store_loads = {"Store A": st.session_state.load_a, "Store B": st.session_state.load_b, "Store C": st.session_state.load_c}
    st.session_state.distances = {"Store A": st.session_state.dist_a, "Store B": st.session_state.dist_b, "Store C": st.session_state.dist_c}
    st.session_state.allocation_inventory = {"Store A": st.session_state.alloc_inv_a, "Store B": st.session_state.alloc_inv_b, "Store C": st.session_state.alloc_inv_c}
    st.session_state.balance_inventory = {"Store A": st.session_state.balance_a, "Store B": st.session_state.balance_b, "Store C": st.session_state.balance_c}
    st.session_state.picking_frequency = {"Milk": st.session_state.picks_milk, "Bread": st.session_state.picks_bread, "Chips": st.session_state.picks_chips, "Juice": st.session_state.picks_juice}
    st.session_state.demand_units = st.session_state.demand_units_input
    st.session_state.capacity_units = st.session_state.capacity_units_input
    st.session_state.expected_item = st.session_state.expected_item_input
    st.session_state.scanned_item = st.session_state.scanned_item_input


def call_api(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{st.session_state.backend_url}{path}", json=payload, timeout=12)
    response.raise_for_status()
    return response.json()


def load_sample_rows() -> List[Dict[str, str]]:
    data_path = Path(__file__).resolve().parents[1] / "data" / "sample_data.csv"
    with data_path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def build_allocation_payload() -> Dict[str, Any]:
    return {
        "store_load": [
            {"store": "Store A", "load": st.session_state.store_loads["Store A"]},
            {"store": "Store B", "load": st.session_state.store_loads["Store B"]},
            {"store": "Store C", "load": st.session_state.store_loads["Store C"]},
        ],
        "distance": st.session_state.distances,
        "inventory": st.session_state.allocation_inventory,
    }


def build_inventory_payload() -> Dict[str, Any]:
    return {"stock_levels": st.session_state.balance_inventory}


def build_layout_payload() -> Dict[str, Any]:
    return {"picking_frequency": st.session_state.picking_frequency}


def calculate_metrics(results: Dict[str, Any]) -> Dict[str, float]:
    demand_level = results.get("demand", {}).get("demand_level", "LOW")
    demand_score = {"LOW": 35, "MEDIUM": 67, "HIGH": 92}.get(demand_level, 35)
    allocation = results.get("allocation", {}).get("result", {})
    selected_store = allocation.get("selected_store", "Store A")
    load_before = max(st.session_state.store_loads.values())
    load_after = st.session_state.store_loads.get(selected_store, load_before)
    load_reduction = max(0.0, round(load_before - load_after, 1))
    error_status = results.get("error", {}).get("result", {}).get("status", "success")
    picking_efficiency = 88.0 if error_status == "success" else 82.0
    if results.get("layout", {}).get("result", {}).get("new_shelf_positions"):
        picking_efficiency += 7.0
    picking_efficiency = min(99.0, round(picking_efficiency, 1))
    capacity_active = results.get("capacity", {}).get("result", {}).get("activate_ghost_store", False)
    system_health = 99.7 if not capacity_active else 95.2
    return {
        "demand_score": demand_score,
        "load_reduction": load_reduction,
        "picking_efficiency": picking_efficiency,
        "system_health": system_health,
    }


def build_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    demand_level = results.get("demand", {}).get("demand_level", "LOW")
    high_load = results.get("capacity", {}).get("result", {}).get("activate_ghost_store", False)
    return {
        "system_status": "High Load" if demand_level == "HIGH" or high_load else "Stable",
        "active_agents": len(results),
        "current_demand_level": demand_level,
    }


def render_step_feed(steps: List[Dict[str, str]]) -> None:
    st.markdown("<div class='section-title'>Live Execution Feed</div>", unsafe_allow_html=True)
    for step in steps:
        if step["tone"] == "green":
            st.success(step["message"])
        elif step["tone"] == "yellow":
            st.warning(step["message"])
        elif step["tone"] == "red":
            st.error(step["message"])
        else:
            st.info(step["message"])


def run_full_simulation() -> None:
    st.session_state.last_simulation_error = ""
    sync_from_widgets()
    results: Dict[str, Any] = {}
    steps: List[Dict[str, str]] = []
    progress = st.progress(0, text="Initializing orchestration...")
    feed = st.empty()
    ordered_calls = [
        ("demand", "/predict-demand", {"rainfall": st.session_state.rainfall, "festival": st.session_state.festival}, "DEMAND"),
        ("allocation", "/allocate-store", build_allocation_payload(), "ALLOCATION"),
        ("inventory", "/balance-inventory", build_inventory_payload(), "INVENTORY"),
        ("layout", "/optimize-layout", build_layout_payload(), "LAYOUT"),
        ("capacity", "/activate-capacity", {"demand": st.session_state.demand_units, "capacity": st.session_state.capacity_units}, "CAPACITY"),
        ("error", "/check-error", {"expected_item": st.session_state.expected_item, "scanned_item": st.session_state.scanned_item}, "ERROR CHECK"),
    ]
    try:
        for index, (name, path, payload, short) in enumerate(ordered_calls, start=1):
            result = call_api(path, payload)
            results[name] = result
            if name == "demand":
                level = result["demand_level"]
                msg = f"Step {index} -> Demand Detected ({level})"
                tone = "red" if level == "HIGH" else "yellow" if level == "MEDIUM" else "green"
            elif name == "allocation":
                msg = f"Step {index} -> Store Allocated ({result['result']['selected_store']})"
                tone = "blue"
            elif name == "inventory":
                transfer = bool(result["result"]["actions"])
                msg = "Step 3 -> Inventory Balanced" if transfer else "Step 3 -> Inventory Already Balanced"
                tone = "yellow" if transfer else "green"
            elif name == "layout":
                msg = "Step 4 -> Layout Optimized"
                tone = "blue"
            elif name == "capacity":
                active = result["result"]["activate_ghost_store"]
                msg = "Step 5 -> Capacity Activated" if active else "Step 5 -> Capacity Within Limits"
                tone = "red" if active else "green"
            else:
                success = result["result"]["status"] == "success"
                msg = "Step 6 -> Error Prevented" if success else "Step 6 -> Picking Error Detected"
                tone = "green" if success else "red"
            steps.append({"short": short, "message": msg, "tone": tone})
            progress.progress(int(index / len(ordered_calls) * 100), text=msg)
            with feed.container():
                render_step_feed(steps)
            time.sleep(0.15)
        st.session_state.simulation_results = results
        st.session_state.workflow_steps = steps
        st.session_state.metrics = calculate_metrics(results)
        st.session_state.summary = build_summary(results)
        progress.progress(100, text="Full simulation complete")
    except requests.RequestException as exc:
        st.session_state.last_simulation_error = str(exc)
        progress.empty()


def reset_dashboard() -> None:
    st.session_state.selected_scenario = "Normal Day"
    apply_selected_scenario()
    st.session_state.simulation_results = {}
    st.session_state.workflow_steps = []
    st.session_state.last_simulation_error = ""
    st.session_state.metrics = {"demand_score": 35, "load_reduction": 0.0, "picking_efficiency": 91.0, "system_health": 99.7}
    st.session_state.summary = {"system_status": "Stable", "active_agents": 0, "current_demand_level": "LOW"}


def top_cards(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    demand = results.get("demand", {}).get("demand_level", st.session_state.summary["current_demand_level"])
    store = results.get("allocation", {}).get("result", {}).get("selected_store", "Store 2")
    transfer_actions = results.get("inventory", {}).get("result", {}).get("actions", [])
    transfer_units = transfer_actions[0]["units"] if transfer_actions else 0
    ghost = results.get("capacity", {}).get("result", {}).get("activate_ghost_store", False)
    prevented = results.get("error", {}).get("result", {}).get("status", "success")
    return [
        {"label": "Demand Risk", "value": demand, "subtext": "Rain + Festival" if st.session_state.festival else "Normal Day", "tone": "pink", "bar": st.session_state.metrics["demand_score"]},
        {"label": "Store Assignment", "value": store.replace("Store ", "00"), "subtext": "Optimized Node", "tone": "cyan", "bar": 58},
        {"label": "Inventory Transfer", "value": f"{transfer_units}u", "subtext": "Active Flow", "tone": "mint", "bar": 68 if transfer_actions else 28},
        {"label": "Shelf Optimization", "value": f"+{st.session_state.metrics['picking_efficiency'] - 71:.0f}%", "subtext": "Layout Velocity", "tone": "violet", "bar": st.session_state.metrics["picking_efficiency"]},
        {"label": "Ghost Store", "value": "ACTIVE" if ghost else "READY", "subtext": "Virtual Buffer", "tone": "gold", "bar": 92 if ghost else 44},
        {"label": "Error Detection", "value": "100%", "subtext": "Prevented" if prevented == "error" else "Verified", "tone": "orange", "bar": 100},
    ]


def agent_cards(results: Dict[str, Any]) -> List[Dict[str, str]]:
    store = results.get("allocation", {}).get("result", {}).get("selected_store", "Store B")
    transfer_actions = results.get("inventory", {}).get("result", {}).get("actions", [])
    transfer_units = transfer_actions[0]["units"] if transfer_actions else 0
    ghost = results.get("capacity", {}).get("result", {}).get("activate_ghost_store", False)
    err = results.get("error", {}).get("result", {}).get("status", "success")
    demand = results.get("demand", {}).get("demand_level", st.session_state.summary["current_demand_level"])
    return [
        {"tone": "pink", "badge": f"RISK: {demand}", "title": "Demand Prediction", "desc": f"Predicting demand surge from rainfall {st.session_state.rainfall} and festival mode {'active' if st.session_state.festival else 'inactive'}.", "left": "FORECAST", "right": f"+{st.session_state.metrics['demand_score']}%"},
        {"tone": "cyan", "badge": "STORE 2", "title": "Store Allocation", "desc": f"Routing priority fleet to {store} based on geo-fenced demand and available inventory.", "left": "DISTANCE", "right": f"{min(st.session_state.distances.values()):.1f} KM"},
        {"tone": "mint", "badge": "OPTIMIZING", "title": "Inventory Balancing", "desc": f"Transferring {transfer_units} units between regional nodes to protect fill rate." if transfer_actions else "Stock already balanced across regional nodes.", "left": "TRANSFER", "right": f"{transfer_units} UNITS"},
        {"tone": "violet", "badge": "DYNAMIC", "title": "Shelf Optimization", "desc": "Highlighting fast movers for front-facing pick priority and improved route velocity.", "left": "EFFICIENCY", "right": f"+{st.session_state.metrics['picking_efficiency'] - 71:.0f}%"},
        {"tone": "gold", "badge": "SCALED" if ghost else "READY", "title": "Capacity Scaling", "desc": "Spinning up ghost store virtual buffer." if ghost else "Current capacity is within safe operating range.", "left": "BUFFER", "right": "ACTIVE" if ghost else "STABLE"},
        {"tone": "orange", "badge": "SECURE", "title": "Error Detection", "desc": "Scan mismatch prevented before dispatch." if err == "error" else "Pick validated and dispatch released.", "left": "ACCURACY", "right": "100%"},
    ]


def render_top_cards(results: Dict[str, Any]) -> None:
    cols = st.columns(6)
    for col, card in zip(cols, top_cards(results)):
        with col:
            st.markdown(
                f"<div class='metric-card tone-{card['tone']}'><div class='metric-label'>{card['label']}</div><div class='metric-value'>{card['value']}</div><div class='metric-subtext'>{card['subtext']}</div><div class='metric-bar'><span style='width:{card['bar']}%'></span></div></div>",
                unsafe_allow_html=True,
            )


def render_agent_cards(results: Dict[str, Any]) -> None:
    cols = st.columns(6)
    for col, card in zip(cols, agent_cards(results)):
        with col:
            st.markdown(
                f"<div class='agent-card tone-{card['tone']}'><div class='agent-badge'>{card['badge']}</div><div class='agent-title'>{card['title']}</div><div class='agent-desc'>{card['desc']}</div><div class='agent-visual'></div><div class='agent-footer'><span>{card['left']}</span><span>{card['right']}</span></div></div>",
                unsafe_allow_html=True,
            )


def render_pipeline(steps: List[Dict[str, str]]) -> None:
    cards = "".join(
        f"<div class='flow-stage'><div class='flow-step'>{step['short']}</div><div class='flow-note'>{step['message']}</div></div>"
        for step in steps
    )
    st.markdown("<div class='section-title'>Autonomous Supply Chain Pipeline</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='pipeline-shell'><div><div class='pipeline-row'>"
        + cards
        + "</div></div><div class='health-box'><div class='health-label'>SYSTEM HEALTH</div><div class='health-value'>"
        + f"{st.session_state.metrics['system_health']}%"
        + "</div><div class='health-caption'>A self-healing, autonomous supply chain powered by collaborative AI agents.</div></div></div>",
        unsafe_allow_html=True,
    )


def render_summary() -> None:
    st.markdown("<div class='section-title'>System Summary</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Demand Score", st.session_state.metrics["demand_score"])
    c2.metric("Load Reduction", f"{st.session_state.metrics['load_reduction']}%")
    c3.metric("Picking Efficiency", f"{st.session_state.metrics['picking_efficiency']}%")
    line = (
        f"Overall system status: {st.session_state.summary['system_status']} | "
        f"Active agents: {st.session_state.summary['active_agents']} | "
        f"Current demand level: {st.session_state.summary['current_demand_level']}"
    )
    if st.session_state.summary["system_status"] == "Stable":
        st.success(line)
    else:
        st.warning(line)


def render_controls() -> None:
    st.markdown("<div class='brand-mark'>MALO</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>AUTONOMOUS ORCHESTRATOR</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("Run Full Demo", use_container_width=True, type="primary"):
        run_full_simulation()
    if st.button("Reset", use_container_width=True):
        reset_dashboard()
    st.markdown("<div class='nav-item active'>Fleet Overview</div>", unsafe_allow_html=True)
    st.markdown("<div class='nav-item'>Agent Logistics</div>", unsafe_allow_html=True)
    st.markdown("<div class='nav-item'>Network Nodes</div>", unsafe_allow_html=True)
    st.markdown("<div class='nav-item'>System Logs</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-label'>Environment: Weather</div>", unsafe_allow_html=True)
    st.selectbox("Weather", ["Clear", "Rain", "Storm"], index=1 if st.session_state.rainfall >= 35 else 0, label_visibility="collapsed")
    st.markdown("<div class='panel-label'>Scenario Preset</div>", unsafe_allow_html=True)
    st.selectbox("Scenario", list(SCENARIO_PRESETS.keys()), key="selected_scenario", on_change=apply_selected_scenario, label_visibility="collapsed")
    st.markdown("<div class='panel-label'>Festival Mode</div>", unsafe_allow_html=True)
    st.toggle("Festival", key="festival", label_visibility="collapsed")
    st.markdown("<div class='panel-label'>Rainfall</div>", unsafe_allow_html=True)
    st.slider("Rainfall", 0, 120, key="rainfall_input", label_visibility="collapsed")
    st.markdown("<div class='live-status'>Live Engine Connected</div>", unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        "<div class='hero-header'><div><div class='hero-title'>MALO</div><div class='hero-subtitle'>Multi-Agent Autonomous Logistics Orchestrator</div><div class='hero-caption'>AI AGENTS COLLABORATING IN REAL-TIME</div></div><div class='hero-actions'><div class='demo-pill'>DEMO MODE</div><div class='icon-pill'>ALERT</div><div class='icon-pill'>CFG</div><div class='icon-pill'>LIVE</div></div></div>",
        unsafe_allow_html=True,
    )


def render_manual_controls() -> None:
    with st.expander("Advanced Simulation Controls", expanded=False):
        st.text_input("Backend URL", key="backend_url")
        r1 = st.columns(3)
        r2 = st.columns(3)
        r3 = st.columns(3)
        r4 = st.columns(4)
        r1[0].number_input("Store A Load", min_value=0.0, max_value=100.0, key="load_a", step=5.0)
        r1[1].number_input("Store B Load", min_value=0.0, max_value=100.0, key="load_b", step=5.0)
        r1[2].number_input("Store C Load", min_value=0.0, max_value=100.0, key="load_c", step=5.0)
        r2[0].number_input("Store A Distance", min_value=0.0, key="dist_a", step=0.5)
        r2[1].number_input("Store B Distance", min_value=0.0, key="dist_b", step=0.5)
        r2[2].number_input("Store C Distance", min_value=0.0, key="dist_c", step=0.5)
        r3[0].number_input("Store A Inventory", min_value=0, key="alloc_inv_a", step=1)
        r3[1].number_input("Store B Inventory", min_value=0, key="alloc_inv_b", step=1)
        r3[2].number_input("Store C Inventory", min_value=0, key="alloc_inv_c", step=1)
        r4[0].number_input("Milk Picks", min_value=0, key="picks_milk", step=1)
        r4[1].number_input("Bread Picks", min_value=0, key="picks_bread", step=1)
        r4[2].number_input("Chips Picks", min_value=0, key="picks_chips", step=1)
        r4[3].number_input("Juice Picks", min_value=0, key="picks_juice", step=1)
        b1, b2, b3 = st.columns(3)
        b1.number_input("Balance A", min_value=0, key="balance_a", step=1)
        b2.number_input("Balance B", min_value=0, key="balance_b", step=1)
        b3.number_input("Balance C", min_value=0, key="balance_c", step=1)
        d1, d2 = st.columns(2)
        d1.number_input("Demand Units", min_value=0, key="demand_units_input", step=5)
        d2.number_input("Capacity Units", min_value=0, key="capacity_units_input", step=5)
        e1, e2 = st.columns(2)
        e1.text_input("Expected Item", key="expected_item_input")
        e2.text_input("Scanned Item", key="scanned_item_input")
        if st.button("Apply Manual Changes", use_container_width=True):
            sync_from_widgets()
            st.success("Simulation inputs updated.")
        if st.session_state.simulation_results:
            st.json(st.session_state.simulation_results)


st.markdown(
    """
    <style>
    .stApp {background: radial-gradient(circle at top, #161a33 0%, #0a0d18 45%, #05070e 100%); color: #f5f3ff;}
    .block-container {max-width: 1540px; padding-top: 1.2rem; padding-bottom: 1.2rem;}
    #MainMenu, header, footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .brand-mark {font-size: 2.2rem; font-weight: 900; color: #d8b4fe; letter-spacing: 0.04em;}
    .brand-sub {font-size: 0.82rem; color: #9ca3af; letter-spacing: 0.26em; margin-bottom: 1rem;}
    .nav-item {padding: 0.95rem 1rem; border-radius: 14px; color: #b9bfd1; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); margin: 0.55rem 0; font-weight: 700;}
    .nav-item.active {background: linear-gradient(90deg, rgba(167,139,250,0.22), rgba(167,139,250,0.07)); color: #f3e8ff; border-color: rgba(216,180,254,0.32);}
    .panel-label {margin-top: 1rem; margin-bottom: 0.45rem; color: #a1a1aa; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.18em;}
    .live-status {margin-top: 1.2rem; color: #a7f3d0; font-weight: 700;}
    .hero-header {display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding-bottom: 1rem; margin-bottom: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.05);}
    .hero-title {font-size: 2.2rem; line-height: 1; font-weight: 900; color: #d8b4fe;}
    .hero-subtitle {font-size: 1.45rem; color: #e5e7eb; font-weight: 700; margin-top: 0.1rem;}
    .hero-caption {font-size: 0.82rem; letter-spacing: 0.34em; color: #9ca3af; margin-top: 0.35rem;}
    .hero-actions {display: flex; gap: 0.7rem;}
    .demo-pill, .icon-pill {padding: 0.9rem 1rem; border-radius: 18px; background: rgba(17,24,39,0.72); color: #f3e8ff; border: 1px solid rgba(216,180,254,0.18); font-weight: 800; font-size: 0.8rem;}
    .icon-pill {color: #d1d5db; border-color: rgba(255,255,255,0.08);}
    .metric-card, .agent-card, .pipeline-shell, .side-shell {background: linear-gradient(180deg, rgba(20,24,44,0.96) 0%, rgba(16,20,36,0.96) 100%); border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 18px 40px rgba(0,0,0,0.22);}
    .side-shell {border-radius: 24px; padding: 1.5rem 1.2rem; min-height: 92vh;}
    .metric-card {border-radius: 24px; min-height: 170px; padding: 1rem; margin-bottom: 0.8rem; position: relative; overflow: hidden;}
    .metric-card::after {content: ''; position: absolute; right: -28px; top: -28px; width: 86px; height: 86px; border-radius: 22px; background: rgba(255,255,255,0.04);}
    .metric-label {font-size: 0.74rem; color: #d1d5db; text-transform: uppercase; letter-spacing: 0.18em; margin-bottom: 0.9rem;}
    .metric-value {font-size: 2.05rem; font-weight: 900; line-height: 1.1;}
    .metric-subtext {color: #9ca3af; margin-top: 0.35rem; min-height: 36px;}
    .metric-bar {margin-top: 1rem; width: 100%; height: 8px; background: rgba(0,0,0,0.5); border-radius: 999px; overflow: hidden;}
    .metric-bar span {display: block; height: 100%; border-radius: 999px;}
    .agent-card {border-radius: 28px; min-height: 460px; padding: 1.15rem 1rem; margin-bottom: 1rem;}
    .agent-badge {display: inline-block; padding: 0.45rem 0.7rem; border-radius: 12px; background: rgba(255,255,255,0.08); font-size: 0.8rem; font-weight: 800; margin-bottom: 1.15rem;}
    .agent-title {font-size: 1.05rem; font-weight: 800; color: #f3f4f6; min-height: 54px; margin-bottom: 0.65rem;}
    .agent-desc {color: #c9cddd; line-height: 1.65; min-height: 150px; font-size: 0.95rem;}
    .agent-visual {height: 108px; border-radius: 22px; margin-top: 1rem; background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02)); border: 1px solid rgba(255,255,255,0.06);}
    .agent-footer {display: flex; justify-content: space-between; gap: 0.7rem; margin-top: 1rem; font-size: 0.86rem; font-weight: 800; color: #f3f4f6;}
    .section-title {font-size: 1.8rem; font-weight: 900; color: #e9d5ff; margin: 0.8rem 0 1rem 0;}
    .pipeline-shell {display: grid; grid-template-columns: 3fr 1.2fr; gap: 1rem; border-radius: 28px; padding: 1.3rem 1.4rem; margin: 1rem 0;}
    .pipeline-row {display: flex; flex-wrap: wrap; gap: 0.8rem;}
    .flow-stage {min-width: 130px; padding: 0.85rem 0.95rem; border-radius: 18px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);}
    .flow-step {font-size: 0.75rem; color: #d8b4fe; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.3rem;}
    .flow-note {color: #f3f4f6; font-weight: 700; line-height: 1.4;}
    .health-box {border-left: 1px solid rgba(255,255,255,0.05); padding-left: 1rem; display: flex; flex-direction: column; justify-content: center;}
    .health-label {font-size: 0.82rem; color: #a1a1aa; letter-spacing: 0.22em;}
    .health-value {font-size: 3rem; color: #a7f3d0; font-weight: 900; line-height: 1.1; margin: 0.25rem 0;}
    .health-caption {color: #c7cad6; line-height: 1.55;}
    .tone-pink .metric-value, .tone-pink .agent-badge, .tone-pink .agent-footer span:last-child {color: #fb7185;} .tone-pink .metric-bar span {background: #fb7185;}
    .tone-cyan .metric-value, .tone-cyan .agent-badge, .tone-cyan .agent-footer span:last-child {color: #67e8f9;} .tone-cyan .metric-bar span {background: #67e8f9;}
    .tone-mint .metric-value, .tone-mint .agent-badge, .tone-mint .agent-footer span:last-child {color: #a7f3d0;} .tone-mint .metric-bar span {background: #a7f3d0;}
    .tone-violet .metric-value, .tone-violet .agent-badge, .tone-violet .agent-footer span:last-child {color: #d8b4fe;} .tone-violet .metric-bar span {background: #d8b4fe;}
    .tone-gold .metric-value, .tone-gold .agent-badge, .tone-gold .agent-footer span:last-child {color: #facc15;} .tone-gold .metric-bar span {background: #facc15;}
    .tone-orange .metric-value, .tone-orange .agent-badge, .tone-orange .agent-footer span:last-child {color: #fb923c;} .tone-orange .metric-bar span {background: #fb923c;}
    .stButton > button {min-height: 3.15rem; border-radius: 18px; font-weight: 800; background: #111827; color: #f3f4f6; border: 1px solid rgba(255,255,255,0.08);} .stButton > button[kind='primary'] {background: linear-gradient(90deg, #d8b4fe, #a855f7); color: #1b1028; border: 0;}
    .stTextInput input, .stNumberInput input, div[data-baseweb='select'] > div {background: rgba(17,24,39,0.86) !important; color: #f3f4f6 !important; border-radius: 14px !important;}
    @media (max-width: 1200px) {.pipeline-shell {grid-template-columns: 1fr;} .health-box {border-left: 0; border-top: 1px solid rgba(255,255,255,0.05); padding-left: 0; padding-top: 1rem;}}
    </style>
    """,
    unsafe_allow_html=True,
)

init_state()
layout = st.columns([1.05, 3.55], gap="medium")
with layout[0]:
    st.markdown("<div class='side-shell'>", unsafe_allow_html=True)
    render_controls()
    st.markdown("</div>", unsafe_allow_html=True)
with layout[1]:
    render_header()
    render_top_cards(st.session_state.simulation_results)
    render_agent_cards(st.session_state.simulation_results)
    if st.session_state.last_simulation_error:
        st.error(f"Simulation failed: {st.session_state.last_simulation_error}")
    default_steps = [
        {"short": "DEMAND", "message": "Step 1 -> Demand agent ready", "tone": "blue"},
        {"short": "ALLOCATION", "message": "Step 2 -> Store allocation ready", "tone": "blue"},
        {"short": "INVENTORY", "message": "Step 3 -> Inventory balancing ready", "tone": "blue"},
        {"short": "LAYOUT", "message": "Step 4 -> Layout optimization ready", "tone": "blue"},
        {"short": "CAPACITY", "message": "Step 5 -> Capacity agent ready", "tone": "blue"},
        {"short": "ERROR CHECK", "message": "Step 6 -> Error detection ready", "tone": "blue"},
    ]
    active_steps = st.session_state.workflow_steps or default_steps
    render_step_feed(active_steps)
    render_pipeline(active_steps)
    render_summary()
    with st.expander("Sample Store Snapshot", expanded=False):
        st.dataframe(load_sample_rows(), use_container_width=True)
    render_manual_controls()
