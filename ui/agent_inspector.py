"""
RESONA - Agent Inspector

Provides a transparent view of agent roles, execution status,
inputs, outputs, dependencies, tools, and revisions.

The interface intentionally does not expose chain-of-thought.
Only structured operational summaries are displayed.
"""

from typing import Any, Dict, List

import streamlit as st


AGENT_DETAILS = {
    "Situation Intelligence Agent": {
        "role": "Situation Intelligence Specialist",
        "purpose": (
            "Builds structured situational understanding "
            "from emergency information."
        ),
        "inputs": [
            "Emergency context",
            "Location",
            "Affected population",
            "Reported conditions",
        ],
        "outputs": [
            "Affected areas",
            "Severity",
            "Constraints",
            "Missing information",
        ],
    },
    "Needs Assessment Agent": {
        "role": "Emergency Needs Assessment Specialist",
        "purpose": (
            "Identifies humanitarian and operational needs."
        ),
        "inputs": [
            "Situation assessment",
            "Affected areas",
            "Emergency conditions",
        ],
        "outputs": [
            "Need categories",
            "Urgency",
            "Estimated requirements",
            "Information gaps",
        ],
    },
    "Resource Intelligence Agent": {
        "role": "Emergency Resource Intelligence Specialist",
        "purpose": (
            "Compares available resources with identified needs."
        ),
        "inputs": [
            "Available resources",
            "Needs assessment",
            "Resource constraints",
        ],
        "outputs": [
            "Available resources",
            "Shortages",
            "Surplus",
            "Allocation constraints",
        ],
    },
    "Logistics & Deployment Agent": {
        "role": "Emergency Logistics and Deployment Specialist",
        "purpose": (
            "Analyzes accessibility, transportation, and deployment."
        ),
        "inputs": [
            "Resources",
            "Affected areas",
            "Accessibility",
            "Transportation",
        ],
        "outputs": [
            "Deployment options",
            "Bottlenecks",
            "Transport constraints",
            "Deployment sequence",
        ],
    },
    "Priority & Impact Agent": {
        "role": "Emergency Priority and Impact Specialist",
        "purpose": (
            "Analyzes response priority using multiple evidence factors."
        ),
        "inputs": [
            "Population impact",
            "Severity",
            "Urgency",
            "Vulnerability",
            "Resource shortages",
            "Accessibility",
        ],
        "outputs": [
            "Priority areas",
            "Priority reasons",
            "Urgency",
            "Uncertainty",
        ],
    },
    "Critic & Conflict Resolution Agent": {
        "role": "Emergency Response Critic and Conflict Resolution Specialist",
        "purpose": (
            "Reviews agent findings and detects conflicts or "
            "feasibility problems."
        ),
        "inputs": [
            "Situation findings",
            "Needs",
            "Resources",
            "Logistics",
            "Priority analysis",
        ],
        "outputs": [
            "Conflicts",
            "Unsupported assumptions",
            "Feasibility issues",
            "Re-evaluation requirements",
        ],
    },
    "Response Coordinator Agent": {
        "role": "Emergency Response Coordinator",
        "purpose": (
            "Synthesizes reviewed findings into one response plan."
        ),
        "inputs": [
            "Reviewed agent findings",
            "Critic assessment",
            "Resource constraints",
            "Priority analysis",
        ],
        "outputs": [
            "Response plan",
            "Resource allocation",
            "Deployment",
            "Immediate actions",
        ],
    },
}


def _get_history() -> List[Dict[str, Any]]:
    """
    Return current workflow execution history.
    """

    result = st.session_state.get(
        "workflow_result",
        {},
    )

    state = result.get(
        "state",
        {},
    ) or {}

    return state.get(
        "agent_history",
        [],
    ) or []


def render_agent_inspector() -> None:
    """
    Render the agent inspection interface.
    """

    st.markdown(
        """
        <div class="section-label">
            TRANSPARENCY LAYER
        </div>

        <h1 style="margin-top:0;">
            Agent Inspector
        </h1>

        <p style="color:#94a3b8;">
            Inspect what each specialized agent is responsible
            for and review its structured execution record.
        </p>
        """,
        unsafe_allow_html=True,
    )

    history = _get_history()

    names = list(
        AGENT_DETAILS.keys()
    )

    selected = st.selectbox(
        "Select Agent",
        names,
    )

    details = AGENT_DETAILS[
        selected
    ]

    matching_records = [
        record
        for record in history
        if record.get(
            "agent_name"
        ) == selected
    ]

    record = (
        matching_records[-1]
        if matching_records
        else {}
    )

    left, right = st.columns(
        [1, 1],
        gap="large",
    )

    with left:

        st.markdown(
            '<div class="section-label">Agent Identity</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="info-panel">
                <h3 style="margin-top:0;">
                    {selected}
                </h3>

                <p style="color:#38bdf8;">
                    {details["role"]}
                </p>

                <p style="
                    color:#94a3b8;
                    line-height:1.7;
                ">
                    {details["purpose"]}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            "### Inputs"
        )

        for item in details["inputs"]:
            st.markdown(
                f"- {item}"
            )

        st.markdown(
            "### Structured Outputs"
        )

        for item in details["outputs"]:
            st.markdown(
                f"- {item}"
            )

    with right:

        st.markdown(
            '<div class="section-label">Execution</div>',
            unsafe_allow_html=True,
        )

        if not record:
            st.info(
                "This agent has not executed in the current workflow."
            )

            return

        status = record.get(
            "status",
            "unknown",
        )

        revision = record.get(
            "revision",
            0,
        )

        st.markdown(
            f"""
            <div class="info-panel">
                <p>
                    <strong>Status:</strong>
                    {status}
                </p>

                <p>
                    <strong>Revision:</strong>
                    {revision}
                </p>

                <p>
                    <strong>Timestamp:</strong>
                    {record.get("timestamp", "N/A")}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            "### Upstream Agents"
        )

        upstream = record.get(
            "upstream_agents",
            [],
        )

        if upstream:
            for item in upstream:
                st.markdown(
                    f"- {item}"
                )
        else:
            st.caption("None")

        st.markdown(
            "### Downstream Agents"
        )

        downstream = record.get(
            "downstream_agents",
            [],
        )

        if downstream:
            for item in downstream:
                st.markdown(
                    f"- {item}"
                )
        else:
            st.caption("None")

        st.markdown(
            "### Tools Used"
        )

        tools = record.get(
            "tools_used",
            [],
        )

        if tools:
            for item in tools:
                st.markdown(
                    f"- `{item}`"
                )
        else:
            st.caption(
                "No tool execution recorded."
            )

    output = record.get(
        "output_summary",
        "",
    )

    if output:

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="section-label">Output Summary</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="info-panel">
                {output}
            </div>
            """,
            unsafe_allow_html=True,
        )
