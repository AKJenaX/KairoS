from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

import streamlit as st


COLORS = {
    "background": "#B8E3E9",
    "sidebar": "#93B1B5",
    "button": "#4F7C82",
    "header": "#0B2E33",
    "text": "#0B2E33",
    "success": "#16A34A",
    "warning": "#F97316",
    "critical": "#DC2626",
    "card": "#FFFFFF",
}


DEFAULT_METRICS = {
    "system_status": "ACTIVE",
    "active_agents": 6,
    "scenario": "Normal Day",
}


def init_shared_state() -> None:
    if "backend_url" not in st.session_state:
        st.session_state.backend_url = "http://127.0.0.1:8000"
    if "global_metrics" not in st.session_state:
        st.session_state.global_metrics = DEFAULT_METRICS.copy()
    if "selected_agent" not in st.session_state:
        st.session_state.selected_agent = "Demand Prediction"
    if "support_message" not in st.session_state:
        st.session_state.support_message = ""
    if "account_message" not in st.session_state:
        st.session_state.account_message = ""
    if "dashboard_outputs" not in st.session_state:
        st.session_state.dashboard_outputs = {}
    if "inventory_transfers" not in st.session_state:
        st.session_state.inventory_transfers = [
            {
                "Manifest ID": "MNF-9201-B",
                "Source": "Regional Hub South",
                "Destination": "MFC-18 Austin",
                "Quantity": "1,240 Units",
                "ETA": "Today, 14:30",
                "Status": "IN TRANSIT",
            },
            {
                "Manifest ID": "MNF-8842-X",
                "Source": "Global Port Terminal 4",
                "Destination": "MFC-72 Downtown",
                "Quantity": "4,500 Units",
                "ETA": "Tomorrow, 09:00",
                "Status": "PENDING",
            },
        ]


def apply_page_config(page_title: str) -> None:
    st.set_page_config(page_title=page_title, layout="wide")
    init_shared_state()
    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {COLORS["background"]};
            --sidebar: {COLORS["sidebar"]};
            --button: {COLORS["button"]};
            --header: {COLORS["header"]};
            --text: {COLORS["text"]};
            --success: {COLORS["success"]};
            --warning: {COLORS["warning"]};
            --critical: {COLORS["critical"]};
            --card: {COLORS["card"]};
        }}
        .stApp {{
            background: var(--bg);
            color: var(--text);
        }}
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 1500px;
        }}
        [data-testid="stSidebarNav"] {{
            display: none;
        }}
        [data-testid="stSidebar"] {{
            background: var(--sidebar);
            border-right: 1px solid rgba(11, 46, 51, 0.12);
        }}
        [data-testid="stSidebarCollapseButton"] {{
            display: none;
        }}
        #MainMenu, footer, header {{
            visibility: hidden;
        }}
        .malo-header {{
            background: var(--header);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            color: white;
            margin-bottom: 1rem;
        }}
        .malo-brand {{
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1.1;
        }}
        .malo-subbrand {{
            font-size: 0.88rem;
            opacity: 0.85;
        }}
        .nav-link-row {{
            display: flex;
            gap: 1rem;
            align-items: center;
            color: white;
            font-size: 0.86rem;
            font-weight: 600;
        }}
        .card-shell {{
            background: var(--card);
            border-radius: 22px;
            padding: 1rem;
            box-shadow: 0 10px 30px rgba(11, 46, 51, 0.08);
            border: 1px solid rgba(11, 46, 51, 0.06);
            height: 100%;
        }}
        .page-title {{
            font-size: 2.25rem;
            font-weight: 800;
            color: var(--text);
            margin-bottom: 0.1rem;
        }}
        .page-kicker {{
            font-size: 0.78rem;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: rgba(11, 46, 51, 0.6);
            font-weight: 700;
        }}
        .page-subtitle {{
            color: rgba(11, 46, 51, 0.72);
            margin-bottom: 1rem;
        }}
        .section-title {{
            color: var(--text);
            font-size: 1.1rem;
            font-weight: 800;
            margin-bottom: 0.75rem;
        }}
        .metric-card {{
            background: white;
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 28px rgba(11, 46, 51, 0.08);
            border: 1px solid rgba(11, 46, 51, 0.05);
        }}
        .metric-label {{
            color: rgba(11, 46, 51, 0.6);
            font-size: 0.76rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-weight: 700;
        }}
        .metric-value {{
            color: var(--text);
            font-size: 2.2rem;
            font-weight: 800;
            margin-top: 0.35rem;
        }}
        .metric-helper {{
            color: rgba(11, 46, 51, 0.6);
            font-size: 0.86rem;
            margin-top: 0.2rem;
        }}
        .status-badge {{
            display: inline-block;
            padding: 0.28rem 0.55rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.04em;
        }}
        .badge-success {{
            color: var(--success);
            background: rgba(22, 163, 74, 0.12);
        }}
        .badge-warning {{
            color: var(--warning);
            background: rgba(249, 115, 22, 0.12);
        }}
        .badge-critical {{
            color: var(--critical);
            background: rgba(220, 38, 38, 0.12);
        }}
        .badge-neutral {{
            color: var(--button);
            background: rgba(79, 124, 130, 0.14);
        }}
        .hero-panel {{
            background: white;
            border-radius: 24px;
            padding: 1.2rem 1.4rem;
            border: 1px solid rgba(11, 46, 51, 0.08);
            box-shadow: 0 12px 30px rgba(11, 46, 51, 0.08);
            min-height: 220px;
        }}
        .hero-panel.alert {{
            background: rgba(220, 38, 38, 0.12);
            border-color: rgba(220, 38, 38, 0.4);
        }}
        .hero-panel.info {{
            border-color: rgba(11, 46, 51, 0.18);
        }}
        .hero-title {{
            color: rgba(11, 46, 51, 0.68);
            font-size: 0.88rem;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }}
        .hero-value {{
            color: var(--text);
            font-size: 3.6rem;
            font-weight: 900;
            line-height: 1;
            margin-top: 1rem;
        }}
        .hero-copy {{
            color: rgba(11, 46, 51, 0.76);
            font-size: 0.98rem;
            margin-top: 0.9rem;
            line-height: 1.45;
        }}
        .alert-strip {{
            background: rgba(220, 38, 38, 0.12);
            border: 1px solid rgba(220, 38, 38, 0.28);
            border-radius: 24px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 10px 24px rgba(11, 46, 51, 0.08);
        }}
        .alert-strip-title {{
            color: var(--text);
            font-size: 0.92rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }}
        .alert-strip-copy {{
            color: rgba(11, 46, 51, 0.8);
            font-size: 1.05rem;
            margin-top: 0.75rem;
            line-height: 1.5;
        }}
        .recommendation-panel {{
            background: #0B2E33;
            border-radius: 24px;
            padding: 1.3rem 1.5rem;
            box-shadow: 0 12px 28px rgba(11, 46, 51, 0.16);
        }}
        .recommendation-title {{
            color: white;
            font-size: 1.95rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }}
        .recommendation-panel ul {{
            margin: 0;
            padding-left: 1.4rem;
        }}
        .recommendation-panel li {{
            color: white;
            font-size: 1rem;
            margin: 0.8rem 0;
            line-height: 1.6;
        }}
        .action-list {{
            margin: 0;
            padding-left: 1.2rem;
        }}
        .action-list li {{
            margin: 0.5rem 0;
            color: var(--text);
            line-height: 1.5;
        }}
        .stButton > button, .stDownloadButton > button {{
            background: var(--button);
            color: white;
            border: 0;
            border-radius: 14px;
            min-height: 2.9rem;
            font-weight: 700;
            box-shadow: 0 8px 18px rgba(79, 124, 130, 0.2);
        }}
        .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {{
            border-radius: 12px !important;
            border-color: rgba(11, 46, 51, 0.12) !important;
        }}
        .stDataFrame, .stTable {{
            background: white;
            border-radius: 18px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def current_utc_time() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S UTC")


def badge_html(label: str, kind: str) -> str:
    class_name = {
        "success": "badge-success",
        "warning": "badge-warning",
        "critical": "badge-critical",
        "neutral": "badge-neutral",
    }.get(kind, "badge-neutral")
    return f"<span class='status-badge {class_name}'>{label}</span>"


def status_kind(status: str) -> str:
    status = status.upper()
    if status in {"ACTIVE", "OPTIMAL", "OK", "HEALTHY"}:
        return "success"
    if status in {"WARN", "WARNING", "STRESS", "PENDING", "LATENCY"}:
        return "warning"
    if status in {"ERROR", "CRITICAL", "CANNOT", "DOWN"}:
        return "critical"
    return "neutral"


def set_global_status(status: str, scenario: str, active_agents: int) -> None:
    st.session_state.global_metrics = {
        "system_status": status,
        "scenario": scenario,
        "active_agents": active_agents,
    }


def metric_card(label: str, value: str, helper: str = "") -> str:
    return (
        "<div class='metric-card'>"
        f"<div class='metric-label'>{label}</div>"
        f"<div class='metric-value'>{value}</div>"
        f"<div class='metric-helper'>{helper}</div>"
        "</div>"
    )


def get_mock_events() -> List[Dict[str, str]]:
    return [
        {
            "Timestamp": "2026-04-15 14:20:11",
            "Agent Node": "GW-ALPHA-09",
            "Event Description": "Nexus handshake initiated: Port 8080 secure tunnel established.",
            "Status": "OK-200",
            "Trace ID": "TX-9021-XF",
        },
        {
            "Timestamp": "2026-04-15 14:20:08",
            "Agent Node": "UAV-FLIGHT-66",
            "Event Description": "Latent packet loss detected (1.2%). Re-routing neural path via Gateway Delta.",
            "Status": "WRN-408",
            "Trace ID": "TA-8154-LH",
        },
        {
            "Timestamp": "2026-04-15 13:58:44",
            "Agent Node": "FREIGHT-TRUCK-A1",
            "Event Description": "Critical telemetry failure: Sensor array 04 unresponsive. System lockdown active.",
            "Status": "ERR-500",
            "Trace ID": "TX-7728-KA",
        },
        {
            "Timestamp": "2026-04-15 13:55:12",
            "Agent Node": "SYS-KERN-AUTH",
            "Event Description": "Administrative access granted: User 'Nexus_Admin_01'.",
            "Status": "OK-200",
            "Trace ID": "TK-5590-RT",
        },
        {
            "Timestamp": "2026-04-15 13:52:10",
            "Agent Node": "HUB-CHICAGO-04",
            "Event Description": "Bulk inventory manifest synchronized. 1,440 packets validated successfully.",
            "Status": "OK-201",
            "Trace ID": "TL-4432-PP",
        },
    ]
