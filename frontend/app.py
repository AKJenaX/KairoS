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


def init_session_state() -> None:
    """Seed session state once so widgets and simulation share the same values."""
    defaults = SCENARIO_PRESETS["Normal Day"]
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = "Normal Day"
    if "simulation_results" not in st.session_state:
        st.session_state.simulation_results = {}
    if "workflow_steps" not in st.session_state:
        st.session_state.workflow_steps = []
    if "metrics" not in st.session_state:
        st.session_state.metrics = {
            "demand_score": 35,
            "load_reduction": 0.0,
            "picking_efficiency": 91.0,
        }
    if "summary" not in st.session_state:
        st.session_state.summary = {
            "system_status": "Stable",
            "active_agents": 0,
            "current_demand_level": "LOW",
        }
    if "last_simulation_error" not in st.session_state:
        st.session_state.last_simulation_error = ""

    for field, value in defaults.items():
        if field not in st.session_state:
            st.session_state[field] = value


def apply_selected_scenario() -> None:
    """Update all input controls when the preset changes."""
    scenario = SCENARIO_PRESETS[st.session_state.selected_scenario]
    for field, value in scenario.items():
        st.session_state[field] = value
    st.session_state.balance_a = scenario["balance_inventory"]["Store A"]
    st.session_state.balance_b = scenario["balance_inventory"]["Store B"]
    st.session_state.balance_c = scenario["balance_inventory"]["Store C"]
    st.session_state.load_a = scenario["store_loads"]["Store A"]
    st.session_state.load_b = scenario["store_loads"]["Store B"]
    st.session_state.load_c = scenario["store_loads"]["Store C"]
    st.session_state.dist_a = scenario["distances"]["Store A"]
    st.session_state.dist_b = scenario["distances"]["Store B"]
    st.session_state.dist_c = scenario["distances"]["Store C"]
    st.session_state.alloc_inv_a = scenario["allocation_inventory"]["Store A"]
    st.session_state.alloc_inv_b = scenario["allocation_inventory"]["Store B"]
    st.session_state.alloc_inv_c = scenario["allocation_inventory"]["Store C"]
    st.session_state.picks_milk = scenario["picking_frequency"]["Milk"]
    st.session_state.picks_bread = scenario["picking_frequency"]["Bread"]
    st.session_state.picks_chips = scenario["picking_frequency"]["Chips"]
    st.session_state.picks_juice = scenario["picking_frequency"]["Juice"]
    st.session_state.demand_units_input = scenario["demand_units"]
    st.session_state.capacity_units_input = scenario["capacity_units"]
    st.session_state.expected_item_input = scenario["expected_item"]
    st.session_state.scanned_item_input = scenario["scanned_item"]


def status_html(label: str, value: str, tone: str) -> str:
    palette = {
        "green": ("#dcfce7", "#166534"),
        "yellow": ("#fef9c3", "#854d0e"),
        "red": ("#fee2e2", "#991b1b"),
        "blue": ("#dbeafe", "#1d4ed8"),
    }
    bg, fg = palette[tone]
    return (
        f"<div style='padding:0.85rem 1rem;border-radius:0.85rem;"
        f"background:{bg};color:{fg};font-weight:600;margin-top:0.5rem;'>"
        f"{label}: {value}</div>"
    )


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
    demand_map = {"LOW": 35, "MEDIUM": 67, "HIGH": 92}
    demand_level = results.get("demand", {}).get("demand_level", "LOW")
    allocation_result = results.get("allocation", {}).get("result", {})
    selected_store = allocation_result.get("selected_store", "Store A")
    load_before = max(st.session_state.store_loads.values())
    selected_load = st.session_state.store_loads.get(selected_store, load_before)
    load_reduction = max(0.0, round(load_before - selected_load, 1))

    error_status = results.get("error", {}).get("result", {}).get("status", "success")
    layout_positions = results.get("layout", {}).get("result", {}).get("new_shelf_positions", [])
    front_loaded_items = sum(
        1 for row in layout_positions if row.get("new_position") in {"Front Shelf", "Mid Shelf"}
    )
    picking_efficiency = 82.0 + (front_loaded_items * 4.0)
    if error_status == "success":
        picking_efficiency += 6.0
    picking_efficiency = min(99.0, round(picking_efficiency, 1))

    return {
        "demand_score": demand_map.get(demand_level, 35),
        "load_reduction": load_reduction,
        "picking_efficiency": picking_efficiency,
    }


def build_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    demand_level = results.get("demand", {}).get("demand_level", "LOW")
    capacity_active = results.get("capacity", {}).get("result", {}).get("activate_ghost_store", False)
    system_status = "High Load" if demand_level == "HIGH" or capacity_active else "Stable"

    return {
        "system_status": system_status,
        "active_agents": len(results),
        "current_demand_level": demand_level,
    }


def render_workflow_story(steps: List[Dict[str, str]]) -> None:
    st.subheader("Workflow Visualization")
    for step in steps:
        line = f"{step['title']}: {step['message']}"
        if step["tone"] == "green":
            st.success(line)
        elif step["tone"] == "yellow":
            st.warning(line)
        elif step["tone"] == "red":
            st.error(line)
        else:
            st.info(line)


def run_full_simulation() -> None:
    """Run all six agents in order and stream the story into the UI."""
    st.session_state.last_simulation_error = ""
    results: Dict[str, Any] = {}
    story_steps: List[Dict[str, str]] = []

    progress = st.progress(0, text="Initializing orchestration...")
    story_placeholder = st.container()

    step_definitions = [
        (
            "demand",
            "/predict-demand",
            {"rainfall": st.session_state.rainfall, "festival": st.session_state.festival},
        ),
        ("allocation", "/allocate-store", build_allocation_payload()),
        ("inventory", "/balance-inventory", build_inventory_payload()),
        ("layout", "/optimize-layout", build_layout_payload()),
        (
            "capacity",
            "/activate-capacity",
            {"demand": st.session_state.demand_units, "capacity": st.session_state.capacity_units},
        ),
        (
            "error",
            "/check-error",
            {
                "expected_item": st.session_state.expected_item,
                "scanned_item": st.session_state.scanned_item,
            },
        ),
    ]

    try:
        for index, (name, path, payload) in enumerate(step_definitions, start=1):
            result = call_api(path, payload)
            results[name] = result

            if name == "demand":
                demand_level = result["demand_level"]
                message = f"Step {index} -> Demand Detected ({demand_level})"
                tone = "red" if demand_level == "HIGH" else "yellow" if demand_level == "MEDIUM" else "green"
            elif name == "allocation":
                selected_store = result["result"]["selected_store"]
                message = f"Step {index} -> Store Allocated ({selected_store})"
                tone = "blue" if selected_store != "No feasible store" else "red"
            elif name == "inventory":
                has_transfer = bool(result["result"]["actions"])
                message = "Step 3 -> Inventory Balanced" if has_transfer else "Step 3 -> Inventory Already Balanced"
                tone = "yellow" if has_transfer else "green"
            elif name == "layout":
                message = "Step 4 -> Layout Optimized"
                tone = "blue"
            elif name == "capacity":
                activated = result["result"]["activate_ghost_store"]
                message = "Step 5 -> Capacity Activated" if activated else "Step 5 -> Capacity Within Limits"
                tone = "warning" if False else "red" if activated else "green"
                tone = "red" if activated else "green"
            else:
                success = result["result"]["status"] == "success"
                message = "Step 6 -> Error Prevented" if success else "Step 6 -> Picking Error Detected"
                tone = "green" if success else "red"

            story_steps.append({"title": f"Agent {index}", "message": message, "tone": tone})
            progress.progress(int(index / len(step_definitions) * 100), text=message)

            with story_placeholder:
                render_workflow_story(story_steps)

            time.sleep(0.15)

        st.session_state.simulation_results = results
        st.session_state.workflow_steps = story_steps
        st.session_state.metrics = calculate_metrics(results)
        st.session_state.summary = build_summary(results)
        progress.progress(100, text="Full simulation complete")
    except requests.RequestException as exc:
        st.session_state.last_simulation_error = str(exc)
        progress.empty()


def render_metrics() -> None:
    st.subheader("Metrics and Analytics")
    metric_cols = st.columns(3)
    metric_cols[0].metric("Demand Score", st.session_state.metrics["demand_score"])
    metric_cols[1].metric("Load Reduction", f"{st.session_state.metrics['load_reduction']}%")
    metric_cols[2].metric("Picking Efficiency", f"{st.session_state.metrics['picking_efficiency']}%")


def render_summary_panel() -> None:
    summary = st.session_state.summary
    st.subheader("System Summary")
    if summary["system_status"] == "Stable":
        st.success(f"Overall System Status: {summary['system_status']}")
    else:
        st.warning(f"Overall System Status: {summary['system_status']}")
    summary_cols = st.columns(2)
    summary_cols[0].info(f"Active Agents Count: {summary['active_agents']}")
    summary_cols[1].info(f"Current Demand Level: {summary['current_demand_level']}")


def render_card_start(title: str, description: str) -> None:
    st.markdown(f"<div class='malo-card'><h3>{title}</h3><p>{description}</p>", unsafe_allow_html=True)


def render_card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_individual_agent_controls() -> None:
    st.header("Manual Agent Controls")
    col_left, col_right = st.columns(2)

    with col_left:
        render_card_start(
            "1. Demand Simulation",
            "Demand Agent detects demand surge using rainfall and festival signals.",
        )
        rainfall = st.slider("Rainfall", min_value=0, max_value=120, key="rainfall")
        festival = st.toggle("Festival day", key="festival")
        if st.button("Run Demand Agent", use_container_width=True):
            try:
                result = call_api("/predict-demand", {"rainfall": rainfall, "festival": festival})
                demand_level = result["demand_level"]
                if demand_level == "HIGH":
                    st.error(f"Demand Level: {demand_level}")
                elif demand_level == "MEDIUM":
                    st.warning(f"Demand Level: {demand_level}")
                else:
                    st.success(f"Demand Level: {demand_level}")
                st.json(result)
            except requests.RequestException as exc:
                st.error(f"Backend request failed: {exc}")
        render_card_end()

        render_card_start(
            "3. Inventory Balancing",
            "Inventory Agent recommends stock transfers to keep stores balanced.",
        )
        inventory_cols = st.columns(3)
        st.session_state.balance_inventory["Store A"] = inventory_cols[0].number_input(
            "Store A Stock",
            min_value=0,
            key="balance_a",
            value=st.session_state.balance_inventory["Store A"],
            step=1,
        )
        st.session_state.balance_inventory["Store B"] = inventory_cols[1].number_input(
            "Store B Stock",
            min_value=0,
            key="balance_b",
            value=st.session_state.balance_inventory["Store B"],
            step=1,
        )
        st.session_state.balance_inventory["Store C"] = inventory_cols[2].number_input(
            "Store C Stock",
            min_value=0,
            key="balance_c",
            value=st.session_state.balance_inventory["Store C"],
            step=1,
        )
        if st.button("Run Inventory Agent", use_container_width=True):
            try:
                result = call_api("/balance-inventory", build_inventory_payload())
                actions = result["result"]["actions"]
                summary = result["result"]["transfer_recommendation"]
                if actions:
                    st.warning(summary)
                else:
                    st.success(summary)
                st.json(result)
            except requests.RequestException as exc:
                st.error(f"Backend request failed: {exc}")
        render_card_end()

        render_card_start(
            "5. Ghost Store Activation",
            "Capacity Agent decides when extra fulfillment capacity should be activated.",
        )
        capacity_cols = st.columns(2)
        st.session_state.demand_units = capacity_cols[0].number_input(
            "Demand Units",
            min_value=0,
            key="demand_units_input",
            value=st.session_state.demand_units,
            step=5,
        )
        st.session_state.capacity_units = capacity_cols[1].number_input(
            "Current Capacity",
            min_value=0,
            key="capacity_units_input",
            value=st.session_state.capacity_units,
            step=5,
        )
        if st.button("Run Capacity Agent", use_container_width=True):
            try:
                result = call_api(
                    "/activate-capacity",
                    {"demand": st.session_state.demand_units, "capacity": st.session_state.capacity_units},
                )
                active = result["result"]["activate_ghost_store"]
                if active:
                    st.error("Capacity Decision: Activate Ghost Store")
                else:
                    st.success("Capacity Decision: No Extra Capacity Needed")
                st.json(result)
            except requests.RequestException as exc:
                st.error(f"Backend request failed: {exc}")
        render_card_end()

    with col_right:
        render_card_start(
            "2. Store Allocation",
            "Store Allocation Agent redirects orders to the best store using load, distance, and inventory.",
        )
        load_cols = st.columns(3)
        dist_cols = st.columns(3)
        inv_cols = st.columns(3)

        st.session_state.store_loads["Store A"] = load_cols[0].number_input(
            "Store A Load (%)",
            min_value=0.0,
            max_value=100.0,
            key="load_a",
            value=st.session_state.store_loads["Store A"],
            step=5.0,
        )
        st.session_state.store_loads["Store B"] = load_cols[1].number_input(
            "Store B Load (%)",
            min_value=0.0,
            max_value=100.0,
            key="load_b",
            value=st.session_state.store_loads["Store B"],
            step=5.0,
        )
        st.session_state.store_loads["Store C"] = load_cols[2].number_input(
            "Store C Load (%)",
            min_value=0.0,
            max_value=100.0,
            key="load_c",
            value=st.session_state.store_loads["Store C"],
            step=5.0,
        )

        st.session_state.distances["Store A"] = dist_cols[0].number_input(
            "Store A Distance (km)",
            min_value=0.0,
            key="dist_a",
            value=st.session_state.distances["Store A"],
            step=0.5,
        )
        st.session_state.distances["Store B"] = dist_cols[1].number_input(
            "Store B Distance (km)",
            min_value=0.0,
            key="dist_b",
            value=st.session_state.distances["Store B"],
            step=0.5,
        )
        st.session_state.distances["Store C"] = dist_cols[2].number_input(
            "Store C Distance (km)",
            min_value=0.0,
            key="dist_c",
            value=st.session_state.distances["Store C"],
            step=0.5,
        )

        st.session_state.allocation_inventory["Store A"] = inv_cols[0].number_input(
            "Store A Inventory",
            min_value=0,
            key="alloc_inv_a",
            value=st.session_state.allocation_inventory["Store A"],
            step=1,
        )
        st.session_state.allocation_inventory["Store B"] = inv_cols[1].number_input(
            "Store B Inventory",
            min_value=0,
            key="alloc_inv_b",
            value=st.session_state.allocation_inventory["Store B"],
            step=1,
        )
        st.session_state.allocation_inventory["Store C"] = inv_cols[2].number_input(
            "Store C Inventory",
            min_value=0,
            key="alloc_inv_c",
            value=st.session_state.allocation_inventory["Store C"],
            step=1,
        )

        if st.button("Run Store Allocation Agent", use_container_width=True):
            try:
                result = call_api("/allocate-store", build_allocation_payload())
                selected_store = result["result"]["selected_store"]
                if selected_store != "No feasible store":
                    st.success(f"Selected Store: {selected_store}")
                else:
                    st.error("Selected Store: No feasible store")
                st.json(result)
            except requests.RequestException as exc:
                st.error(f"Backend request failed: {exc}")
        render_card_end()

        render_card_start(
            "4. Shelf Optimization",
            "Layout Optimization Agent moves fast-moving items closer to the picker.",
        )
        layout_cols = st.columns(4)
        st.session_state.picking_frequency["Milk"] = layout_cols[0].number_input(
            "Milk Picks / hour",
            min_value=0,
            key="picks_milk",
            value=st.session_state.picking_frequency["Milk"],
            step=1,
        )
        st.session_state.picking_frequency["Bread"] = layout_cols[1].number_input(
            "Bread Picks / hour",
            min_value=0,
            key="picks_bread",
            value=st.session_state.picking_frequency["Bread"],
            step=1,
        )
        st.session_state.picking_frequency["Chips"] = layout_cols[2].number_input(
            "Chips Picks / hour",
            min_value=0,
            key="picks_chips",
            value=st.session_state.picking_frequency["Chips"],
            step=1,
        )
        st.session_state.picking_frequency["Juice"] = layout_cols[3].number_input(
            "Juice Picks / hour",
            min_value=0,
            key="picks_juice",
            value=st.session_state.picking_frequency["Juice"],
            step=1,
        )
        if st.button("Run Layout Agent", use_container_width=True):
            try:
                result = call_api("/optimize-layout", build_layout_payload())
                st.success("Layout Status: Shelf positions recalculated")
                st.json(result)
            except requests.RequestException as exc:
                st.error(f"Backend request failed: {exc}")
        render_card_end()

        render_card_start(
            "6. Error Detection",
            "Error Detection Agent blocks picking mistakes before order completion.",
        )
        st.session_state.expected_item = st.text_input(
            "Expected Item",
            key="expected_item_input",
            value=st.session_state.expected_item,
        )
        st.session_state.scanned_item = st.text_input(
            "Scanned Item",
            key="scanned_item_input",
            value=st.session_state.scanned_item,
        )
        if st.button("Run Error Detection Agent", use_container_width=True):
            try:
                result = call_api(
                    "/check-error",
                    {
                        "expected_item": st.session_state.expected_item,
                        "scanned_item": st.session_state.scanned_item,
                    },
                )
                if result["result"]["status"] == "success":
                    st.success(result["result"]["message"])
                else:
                    st.error(result["result"]["message"])
                st.json(result)
            except requests.RequestException as exc:
                st.error(f"Backend request failed: {exc}")
        render_card_end()


init_session_state()

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .malo-card {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1.2rem;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }
    .hero-panel {
        padding: 1.3rem 1.4rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 55%, #ecfeff 100%);
        border: 1px solid #dbeafe;
        margin-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.session_state.backend_url = st.sidebar.text_input("Backend URL", "http://127.0.0.1:8000")

st.title("Multi-Agent Autonomous Logistics Orchestrator (MALO)")
st.caption("A polished quick-commerce simulation dashboard for live demos, hackathons, and agentic workflow storytelling.")

st.markdown(
    """
    <div class='hero-panel'>
        <h3 style='margin-top:0;'>Scenario Control Center</h3>
        <p style='margin-bottom:0;'>Choose a preset, run the full orchestration, and watch all six agents coordinate across demand, allocation, inventory, layout, capacity, and picking quality.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

sample_rows = load_sample_rows()
with st.expander("Sample Store Snapshot", expanded=False):
    st.dataframe(sample_rows, use_container_width=True)

render_metrics()

control_cols = st.columns([1.3, 1, 1])
control_cols[0].selectbox(
    "Scenario Preset",
    options=list(SCENARIO_PRESETS.keys()),
    key="selected_scenario",
    on_change=apply_selected_scenario,
)
control_cols[1].info(f"Festival Mode: {'ON' if st.session_state.festival else 'OFF'}")
control_cols[2].info(f"Configured Rainfall: {st.session_state.rainfall}")

st.header("Full Simulation")
st.info("Run the end-to-end workflow to trigger all six agents in sequence and present the story step by step.")
if st.button("Run Full Simulation", type="primary", use_container_width=True):
    run_full_simulation()

if st.session_state.last_simulation_error:
    st.error(f"Simulation failed: {st.session_state.last_simulation_error}")

if st.session_state.workflow_steps:
    render_workflow_story(st.session_state.workflow_steps)
    if st.session_state.simulation_results:
        with st.expander("Simulation Result Payloads", expanded=False):
            st.json(st.session_state.simulation_results)

render_summary_panel()
render_individual_agent_controls()
