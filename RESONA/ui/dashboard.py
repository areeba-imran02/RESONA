"""
RESONA - Dashboard

Main operational dashboard for emergency response monitoring.
"""

from typing import Any, Dict, List

import streamlit as st


AGENT_NAMES = [
    "Situation Intelligence",
    "Needs Assessment",
    "Resource Intelligence",
    "Logistics & Deployment",
    "Priority & Impact",
    "Critic & Conflict Resolution",
    "Response Coordinator",
]


def _metric_card(
    label: str,
    value: Any,
) -> str:
    return f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """


def render_dashboard(
    workflow_result: Dict[str, Any] | None = None,
) -> None:
    """
    Render the main RESONA operational dashboard.
    """

    st.markdown(
        """
        <div class="section-label">
            RESONA COMMAND CENTER
        </div>
        <h1 style="
            margin-top:0;
            margin-bottom:0.35rem;
        ">
            Emergency Response Dashboard
        </h1>
        <p style="
            color:#94a3b8;
            margin-top:0;
        ">
            Monitor emergency intelligence, agent activity,
            resources, and coordinated response decisions.
        </p>
        """,
        unsafe_allow_html=True,
    )

    state = {}

    if workflow_result:
        state = workflow_result.get(
            "state",
            {},
        ) or {}

    situation = state.get(
        "situation",
        {}
    ) or {}

    affected_population = situation.get(
        "affected_population",
        0,
    )

    affected_areas = situation.get(
        "affected_areas",
        [],
    ) or []

    resources = state.get(
        "resources",
        {}
    ) or {}

    available_resources = resources.get(
        "available_resources",
        [],
    ) or []

    critic = state.get(
        "critic",
        {}
    ) or {}

    conflicts = critic.get(
        "conflicts_detected",
        [],
    ) or []

    columns = st.columns(5)

    metrics = [
        (
            "Emergency Status",
            "ACTIVE" if workflow_result else "READY",
        ),
        (
            "Affected Population",
            f"{affected_population:,}",
        ),
        (
            "Affected Areas",
            len(affected_areas),
        ),
        (
            "Resources",
            len(available_resources),
        ),
        (
            "Conflicts",
            len(conflicts),
        ),
    ]

    for column, (label, value) in zip(
        columns,
        metrics,
    ):
        with column:
            st.markdown(
                _metric_card(
                    label,
                    value,
                ),
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns(
        [1.55, 1],
        gap="large",
    )

    with left:
        st.markdown(
            '<div class="section-label">Agent Network</div>',
            unsafe_allow_html=True,
        )

        for index, agent in enumerate(
            AGENT_NAMES
        ):
            if workflow_result:
                status = "Completed"
                dot = "status-dot"
            else:
                status = "Standby"
                dot = ""

            st.markdown(
                f"""
                <div class="agent-card">
                    <span class="{dot}"></span>
                    <span class="agent-name">
                        {index + 1:02d} &nbsp; {agent}
                    </span>
                    <div class="agent-status">
                        {status}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            '<div class="section-label">System Overview</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-panel">
                <h3 style="margin-top:0;">
                    How RESONA Works
                </h3>

                <p style="color:#94a3b8;line-height:1.7;">
                    Emergency information enters the system and
                    is distributed through specialized agents.
                    Their findings are reviewed for conflicts
                    before the coordinator creates the final
                    response plan.
                </p>

                <div class="workflow-line">
                    <p>
                        <strong>Situation</strong>
                        → <strong>Needs</strong>
                        → <strong>Resources</strong>
                    </p>

                    <p>
                        <strong>Logistics</strong>
                        → <strong>Priority</strong>
                        → <strong>Critic</strong>
                    </p>

                    <p>
                        <strong>Re-evaluation</strong>
                        → <strong>Coordinator</strong>
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "＋  Create Emergency",
            type="primary",
            use_container_width=True,
        ):
            st.session_state[
                "active_page"
            ] = "New Emergency"
            st.rerun()
