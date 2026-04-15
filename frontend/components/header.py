from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from components.theme import badge_html, current_utc_time, status_kind


def render_header(active_nav: str, run_button_key: str, show_run_button: bool = True) -> bool:
    """Render the top enterprise header and return whether the run button was pressed."""
    left, center, right = st.columns([1.3, 2.2, 1.8], gap="medium")
    with left:
        st.markdown(
            """
            <div class="malo-header">
                <div class="malo-brand">MALO</div>
                <div class="malo-subbrand">Multi-Agent Logistics Orchestrator</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with center:
        st.markdown("<div class='malo-header'>", unsafe_allow_html=True)
        nav_cols = st.columns(5)
        nav_cols[0].page_link("app.py", label="Dashboard")
        nav_cols[1].page_link("pages/agents.py", label="Agents")
        nav_cols[2].page_link("pages/logs.py", label="Logs")
        nav_cols[3].page_link("pages/inventory.py", label="Inventory")
        nav_cols[4].page_link("pages/analytics.py", label="Analytics")
        st.markdown("</div>", unsafe_allow_html=True)
    run_clicked = False
    with right:
        st.markdown("<div class='malo-header'>", unsafe_allow_html=True)
        top_cols = st.columns([1.25, 1.3, 1.5, 0.65, 0.75, 0.75])
        if show_run_button:
            run_clicked = top_cols[0].button("Run Simulation", key=run_button_key, use_container_width=True)
        top_cols[1].markdown(
            badge_html(
                f"System {st.session_state.global_metrics['system_status']}",
                status_kind(st.session_state.global_metrics["system_status"]),
            ),
            unsafe_allow_html=True,
        )
        with top_cols[2]:
            components.html(
                f"""
                <div id="malo-live-clock" style="color:white;font-size:0.78rem;font-weight:700;padding-top:0.35rem;white-space:nowrap;">
                    {current_utc_time()}
                </div>
                <script>
                function updateClock() {{
                    const now = new Date();
                    const formatter = new Intl.DateTimeFormat('en-GB', {{
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: false,
                        timeZoneName: 'short'
                    }});
                    const target = window.parent.document.getElementById('malo-live-clock');
                    if (target) {{
                        target.textContent = formatter.format(now);
                    }}
                }}
                updateClock();
                setInterval(updateClock, 1000);
                </script>
                """,
                height=28,
            )
        top_cols[3].markdown("<div class='header-meta-chip'>Bell</div>", unsafe_allow_html=True)
        top_cols[4].markdown("<div class='header-meta-chip'>Settings</div>", unsafe_allow_html=True)
        top_cols[5].markdown("<div class='header-meta-chip'>Profile</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    return run_clicked
