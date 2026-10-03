```python
"""
RESONA
AI-Powered Emergency Response Intelligence Platform

Main Streamlit application entry point.
"""

import sys
from pathlib import Path

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = PROJECT_ROOT / "RESONA"

# Allow imports from both the repository root and the
# RESONA backend folder.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if BACKEND_ROOT.exists() and str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st

from config.settings import (
    APP_TITLE,
    validate_configuration,
)

from crew.workflow import ResonaWorkflow

from ui.styles import inject_styles
from ui.landing import render_landing_page
from ui.dashboard import render_dashboard
from ui.emergency_form import render_emergency_form
from ui.agent_workflow import render_agent_workflow
from ui.agent_inspector import render_agent_inspector
from ui.resources import render_resources
from ui.memory_view import render_memory_view


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL SESSION STATE
# ============================================================

def initialize_session_state():
    defaults = {
        "launched": False,
        "active_page": "Dashboard",
        "pending_emergency": None,
        "workflow_result": None,
        "run_workflow": False,
        "workflow_running": False,
        "last_error": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()
inject_styles()


# ============================================================
# EMERGENCY CONTEXT BUILDER
# ============================================================

def build_emergency_context(emergency: dict) -> str:
    """
    Convert emergency form data into structured context
    for the RESONA multi-agent workflow.
    """

    affected_population = emergency.get(
        "affected_population",
        0,
    )

    try:
        affected_population = int(affected_population or 0)
    except (TypeError, ValueError):
        affected_population = 0

    lines = [
        "RESONA EMERGENCY INTAKE",
        "=" * 32,
        "",
        f"Emergency ID: {emergency.get('emergency_id', 'N/A')}",
        f"Emergency Type: {emergency.get('emergency_type', 'N/A')}",
        f"Severity: {emergency.get('severity', 'N/A')}",
        f"Location: {emergency.get('location', 'N/A')}",
        f"Affected Population: {affected_population:,}",
        "",
        "DESCRIPTION",
        "-" * 20,
        emergency.get(
            "description",
            "No description provided.",
        ),
        "",
        "AVAILABLE RESOURCES",
        "-" * 24,
        f"Food Kits: {emergency.get('food_kits', 0)}",
        f"Water Units: {emergency.get('water_units', 0)}",
        (
            "Emergency Vehicles: "
            f"{emergency.get('emergency_vehicles', 0)}"
        ),
        f"Volunteers: {emergency.get('volunteers', 0)}",
        f"Medical Teams: {emergency.get('medical_teams', 0)}",
        (
            "Shelter Capacity: "
            f"{emergency.get('shelter_capacity', 0)}"
        ),
        "",
        "ADDITIONAL INFORMATION",
        "-" * 28,
        emergency.get(
            "additional_information",
            "No additional information provided.",
        ),
    ]

    affected_areas = emergency.get("affected_areas")

    if affected_areas:
        lines.extend(
            [
                "",
                "AFFECTED AREAS",
                "-" * 20,
            ]
        )

        for area in affected_areas:

            if isinstance(area, dict):

                critical_conditions = area.get(
                    "critical_conditions",
                    [],
                )

                if not isinstance(
                    critical_conditions,
                    list,
                ):
                    critical_conditions = [
                        str(critical_conditions)
                    ]

                lines.extend(
                    [
                        f"Area: {area.get('name', 'Unknown')}",
                        (
                            "Population: "
                            f"{area.get('affected_population', 0)}"
                        ),
                        (
                            "Severity: "
                            f"{area.get('severity', 'unknown')}"
                        ),
                        (
                            "Accessibility: "
                            f"{area.get('accessibility', 'unknown')}"
                        ),
                        (
                            "Conditions: "
                            f"{', '.join(map(str, critical_conditions))}"
                        ),
                        "",
                    ]
                )

            else:
                lines.append(str(area))

    lines.extend(
        [
            "",
            "IMPORTANT WORKFLOW RULES",
            "-" * 28,
            "Analyze the emergency using the specialized agents.",
            "Do not hardcode a final priority.",
            "Do not invent unavailable resources.",
            "Identify uncertainty and information gaps.",
            "Check conflicts between agent recommendations.",
            "Re-evaluate relevant agents when the critic requires it.",
            "The Response Coordinator must produce the final plan.",
        ]
    )

    return "\n".join(lines)


# ============================================================
# WORKFLOW EXECUTION
# ============================================================

def execute_pending_workflow():
    """
    Execute the real RESONA CrewAI workflow.
    """

    emergency = st.session_state.get(
        "pending_emergency"
    )

    if not emergency:
        return

    st.session_state["workflow_running"] = True
    st.session_state["last_error"] = None

    try:

        workflow = ResonaWorkflow()

        emergency_id = emergency.get(
            "emergency_id"
        )

        if not emergency_id:
            emergency_id = (
                "RES-"
                + str(abs(hash(str(emergency))))[:10]
            )

        emergency_context = build_emergency_context(
            emergency
        )

        result = workflow.run(
            emergency_context=emergency_context,
            emergency_id=emergency_id,
        )

        st.session_state["workflow_result"] = result

        if result.get("success"):
            st.session_state["last_error"] = None
        else:
            st.session_state["last_error"] = result.get(
                "error",
                "RESONA workflow failed.",
            )

    except Exception as exc:

        st.session_state["workflow_result"] = {
            "success": False,
            "state": None,
            "final_response": None,
            "error": str(exc),
        }

        st.session_state["last_error"] = str(exc)

    finally:

        st.session_state["workflow_running"] = False
        st.session_state["run_workflow"] = False


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-logo">R</div>
                <div>
                    <div class="sidebar-title">RESONA</div>
                    <div class="sidebar-subtitle">
                        Emergency Response Intelligence
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        pages = [
            ("◈", "Dashboard"),
            ("＋", "Create Emergency"),
            ("◎", "Agent Workflow"),
            ("◉", "Agent Inspector"),
            ("▣", "Resources"),
            ("◌", "Memory"),
        ]

        for icon, page in pages:

            is_active = (
                st.session_state["active_page"]
                == page
            )

            button_label = f"{icon}  {page}"

            if st.button(
                button_label,
                key=f"nav_{page}",
                use_container_width=True,
                type=(
                    "primary"
                    if is_active
                    else "secondary"
                ),
            ):

                st.session_state["active_page"] = page
                st.rerun()

        st.markdown("---")

        st.markdown(
            """
            <div class="sidebar-system">
                <div class="system-dot"></div>
                <div>
                    <strong>RESONA Core</strong>
                    <span>Multi-Agent Intelligence</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "Many Agents. One Coordinated Response."
        )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    # --------------------------------------------------------
    # Landing Page
    # --------------------------------------------------------

    if not st.session_state["launched"]:

        render_landing_page()

        return

    # --------------------------------------------------------
    # Sidebar
    # --------------------------------------------------------

    render_sidebar()

    # --------------------------------------------------------
    # Execute Requested Workflow
    # --------------------------------------------------------

    if (
        st.session_state.get("run_workflow")
        and st.session_state.get("pending_emergency")
        and not st.session_state.get(
            "workflow_running"
        )
    ):

        with st.spinner(
            "RESONA is coordinating its agent team..."
        ):

            execute_pending_workflow()

        st.session_state["active_page"] = (
            "Agent Workflow"
        )

        st.rerun()

    # --------------------------------------------------------
    # Error Banner
    # --------------------------------------------------------

    if st.session_state.get("last_error"):

        st.error(
            "RESONA workflow error: "
            f"{st.session_state['last_error']}"
        )

    # --------------------------------------------------------
    # Current Page
    # --------------------------------------------------------

    page = st.session_state["active_page"]

    workflow_result = st.session_state.get(
        "workflow_result"
    )

    if page == "Dashboard":

        render_dashboard(
            workflow_result=workflow_result
        )

    elif page == "Create Emergency":

        render_emergency_form()

    elif page == "Agent Workflow":

        render_agent_workflow(
            workflow_result=workflow_result
        )

    elif page == "Agent Inspector":

        render_agent_inspector(
            workflow_result=workflow_result
        )

    elif page == "Resources":

        render_resources(
            workflow_result=workflow_result
        )

    elif page == "Memory":

        render_memory_view()

    else:

        render_dashboard(
            workflow_result=workflow_result
        )


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":
    main()
```
