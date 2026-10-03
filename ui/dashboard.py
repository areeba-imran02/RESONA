"""
RESONA - Dashboard UI
"""

import streamlit as st


AGENT_NAMES = [
    "Situation Intelligence Agent",
    "Needs Assessment Agent",
    "Resource Intelligence Agent",
    "Logistics & Deployment Agent",
    "Priority & Impact Agent",
    "Critic & Conflict Resolution Agent",
    "Response Coordinator Agent",
]


def _get_state(workflow_result):
    if not workflow_result:
        return None
    return workflow_result.get("state")


def _get_history(workflow_result):
    state = _get_state(workflow_result)

    if not state:
        return []

    return getattr(state, "agent_history", []) or []


def _get_status(history, agent_name):
    matches = [
        item
        for item in history
        if getattr(item, "agent_name", "") == agent_name
    ]

    if not matches:
        return "Pending"

    return getattr(
        matches[-1],
        "status",
        "Pending",
    ).title()


def _render_metric_card(title, value, subtitle):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(workflow_result=None):
    state = _get_state(workflow_result)

    st.markdown(
        """
        <div class="page-header">
            <div class="page-eyebrow">
                RESONA COMMAND CENTER
            </div>
            <h1>Emergency Response Dashboard</h1>
            <p>
                A unified view of emergency intelligence,
                multi-agent analysis and coordinated response.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # No analysis yet
    # --------------------------------------------------------

    if not state:

        cols = st.columns(4)

        with cols[0]:
            _render_metric_card(
                "AGENTS",
                "07",
                "Specialized AI agents",
            )

        with cols[1]:
            _render_metric_card(
                "MEMORY",
                "2-LAYER",
                "Short + long term",
            )

        with cols[2]:
            _render_metric_card(
                "REVIEW",
                "ACTIVE",
                "Conflict detection",
            )

        with cols[3]:
            _render_metric_card(
                "STATUS",
                "READY",
                "System initialized",
            )

        st.markdown("---")

        st.markdown(
            """
            <div class="dashboard-empty">
                <div class="dashboard-empty-icon">◈</div>
                <h2>No active emergency analysis</h2>
                <p>
                    Create an emergency scenario to activate
                    the RESONA multi-agent response system.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "＋ Create Emergency",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["active_page"] = (
                "Create Emergency"
            )
            st.rerun()

        return

    # --------------------------------------------------------
    # Active analysis
    # --------------------------------------------------------

    situation = getattr(
        state,
        "situation",
        None,
    )

    critic = getattr(
        state,
        "critic",
        None,
    )

    final_response = getattr(
        state,
        "final_response",
        None,
    )

    history = _get_history(
        workflow_result
    )

    population = (
        getattr(
            situation,
            "affected_population",
            0,
        )
        if situation
        else 0
    )

    priority_count = (
        len(
            getattr(
                final_response,
                "priority_areas",
                [],
            )
        )
        if final_response
        else 0
    )

    conflict_count = (
        len(
            getattr(
                critic,
                "conflicts_detected",
                [],
            )
        )
        if critic
        else 0
    )

    revision_count = getattr(
        state,
        "revision_count",
        0,
    )

    cols = st.columns(4)

    with cols[0]:
        _render_metric_card(
            "AFFECTED",
            f"{population:,}",
            "People identified",
        )

    with cols[1]:
        _render_metric_card(
            "PRIORITIES",
            str(priority_count),
            "Response priority areas",
        )

    with cols[2]:
        _render_metric_card(
            "CONFLICTS",
            str(conflict_count),
            "Detected by critic",
        )

    with cols[3]:
        _render_metric_card(
            "REVISIONS",
            str(revision_count),
            "Agent re-evaluations",
        )

    st.markdown("---")

    # --------------------------------------------------------
    # Emergency overview
    # --------------------------------------------------------

    st.markdown(
        "### Emergency Intelligence"
    )

    col1, col2 = st.columns([1, 1])

    with col1:

        st.markdown(
            """
            <div class="dashboard-panel">
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Situation")

        if situation:

            st.write(
                f"**Emergency:** "
                f"{situation.emergency_type}"
            )

            st.write(
                f"**Location:** "
                f"{situation.location}"
            )

            st.write(
                f"**Severity:** "
                f"{situation.overall_severity.title()}"
            )

            st.write(
                f"**Affected population:** "
                f"{situation.affected_population:,}"
            )

        else:
            st.info(
                "Situation assessment unavailable."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="dashboard-panel">
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Workflow")

        status = getattr(
            state,
            "workflow_status",
            "unknown",
        )

        st.write(
            f"**System status:** "
            f"{status.title()}"
        )

        st.write(
            f"**Agents executed:** "
            f"{len(history)}"
        )

        st.write(
            f"**Workflow revisions:** "
            f"{revision_count}"
        )

        st.write(
            "**Architecture:** "
            "Sequential analysis + critic review + coordination"
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --------------------------------------------------------
    # Agent status
    # --------------------------------------------------------

    st.markdown(
        "### Agent Network Status"
    )

    for index, agent_name in enumerate(
        AGENT_NAMES,
        start=1,
    ):

        status = _get_status(
            history,
            agent_name,
        )

        if status.lower() in {
            "completed",
            "reviewed",
            "revised",
        }:
            icon = "✓"
        elif status.lower() == "failed":
            icon = "×"
        else:
            icon = "○"

        col1, col2, col3 = st.columns(
            [0.5, 5, 2]
        )

        with col1:
            st.markdown(
                f"**{index:02d}**"
            )

        with col2:
            st.markdown(
                f"**{agent_name}**"
            )

        with col3:
            st.markdown(
                f"`{icon} {status}`"
            )

    st.markdown("---")

    # --------------------------------------------------------
    # Final response preview
    # --------------------------------------------------------

    if final_response:

        st.markdown(
            "### Coordinated Response"
        )

        st.success(
            getattr(
                final_response,
                "emergency_summary",
                "Final response generated.",
            )
        )

        immediate_actions = getattr(
            final_response,
            "immediate_actions",
            [],
        )

        if immediate_actions:

            st.markdown(
                "#### Immediate Actions"
            )

            for action in immediate_actions[:5]:
                st.markdown(
                    f"• {action}"
                )

        if st.button(
            "◎ Open Agent Workflow",
            use_container_width=True,
        ):
            st.session_state["active_page"] = (
                "Agent Workflow"
            )
            st.rerun()
