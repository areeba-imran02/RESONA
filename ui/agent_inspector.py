"""
RESONA - Agent Inspector UI
"""

import streamlit as st


AGENT_DETAILS = {
    "Situation Intelligence Agent": {
        "role": "Situation Intelligence",
        "purpose": "Builds the operational picture of the emergency.",
        "inputs": "Emergency type, location, severity, population and conditions.",
        "outputs": "SituationAssessment",
        "upstream": "Emergency Intake",
        "downstream": "Needs Assessment",
    },
    "Needs Assessment Agent": {
        "role": "Needs Assessment",
        "purpose": "Identifies humanitarian and operational needs.",
        "inputs": "Situation assessment.",
        "outputs": "NeedsAssessment",
        "upstream": "Situation Intelligence",
        "downstream": "Resource Intelligence",
    },
    "Resource Intelligence Agent": {
        "role": "Resource Intelligence",
        "purpose": "Analyzes available resources and shortages.",
        "inputs": "Situation + needs.",
        "outputs": "ResourceAssessment",
        "upstream": "Situation, Needs",
        "downstream": "Logistics",
    },
    "Logistics & Deployment Agent": {
        "role": "Logistics & Deployment",
        "purpose": "Evaluates transportation and deployment feasibility.",
        "inputs": "Situation, needs and resources.",
        "outputs": "LogisticsAssessment",
        "upstream": "Situation, Needs, Resources",
        "downstream": "Priority",
    },
    "Priority & Impact Agent": {
        "role": "Priority & Impact",
        "purpose": "Analyzes transparent response-priority factors.",
        "inputs": "Needs, resources and logistics.",
        "outputs": "PriorityAssessment",
        "upstream": "Needs, Resources, Logistics",
        "downstream": "Critic",
    },
    "Critic & Conflict Resolution Agent": {
        "role": "Critic & Conflict Resolution",
        "purpose": "Challenges findings and identifies conflicts.",
        "inputs": "All previous assessments.",
        "outputs": "CriticAssessment",
        "upstream": "Situation, Needs, Resources, Logistics, Priority",
        "downstream": "Re-evaluation / Coordinator",
    },
    "Response Coordinator Agent": {
        "role": "Response Coordinator",
        "purpose": "Synthesizes reviewed findings into a response plan.",
        "inputs": "Final reviewed multi-agent analysis.",
        "outputs": "ResponsePlan",
        "upstream": "Critic + reviewed assessments",
        "downstream": "Final Response",
    },
}


def _get_history(workflow_result):
    if not workflow_result:
        return []

    state = workflow_result.get("state")

    if not state:
        return []

    return getattr(
        state,
        "agent_history",
        [],
    ) or []


def _get_records(history, agent_name):
    return [
        record
        for record in history
        if getattr(
            record,
            "agent_name",
            "",
        ) == agent_name
    ]


def render_agent_inspector(workflow_result=None):

    st.markdown(
        """
        <div class="page-header">
            <div class="page-eyebrow">
                AGENT INTELLIGENCE
            </div>
            <h1>Agent Inspector</h1>
            <p>
                Inspect each specialized agent's role,
                execution status and structured output summary.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = _get_history(
        workflow_result
    )

    selected_agent = st.selectbox(
        "Select Agent",
        list(AGENT_DETAILS.keys()),
    )

    details = AGENT_DETAILS[
        selected_agent
    ]

    records = _get_records(
        history,
        selected_agent,
    )

    latest = (
        records[-1]
        if records
        else None
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Role",
            details["role"],
        )

    with col2:
        status = (
            getattr(
                latest,
                "status",
                "Pending",
            ).title()
            if latest
            else "Pending"
        )

        st.metric(
            "Status",
            status,
        )

    with col3:
        revision = (
            getattr(
                latest,
                "revision",
                0,
            )
            if latest
            else 0
        )

        st.metric(
            "Revision",
            revision,
        )

    st.markdown("---")

    st.markdown(
        "### Agent Definition"
    )

    st.write(
        f"**Purpose:** {details['purpose']}"
    )

    st.write(
        f"**Inputs:** {details['inputs']}"
    )

    st.write(
        f"**Structured Output:** `{details['outputs']}`"
    )

    st.write(
        f"**Upstream:** {details['upstream']}"
    )

    st.write(
        f"**Downstream:** {details['downstream']}"
    )

    st.markdown("---")

    st.markdown(
        "### Execution Summary"
    )

    if not latest:

        st.info(
            "This agent has not executed in the current workflow."
        )

        return

    summary = getattr(
        latest,
        "output_summary",
        "",
    )

    timestamp = getattr(
        latest,
        "timestamp",
        None,
    )

    tools = getattr(
        latest,
        "tools_used",
        [],
    )

    st.success(
        summary
        or "Structured output generated."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "**Execution Time**"
        )
        st.caption(
            timestamp
            or "Not available"
        )

    with col2:
        st.markdown(
            "**Tools Used**"
        )

        if tools:
            st.write(
                ", ".join(tools)
            )
        else:
            st.caption(
                "No external tools recorded."
            )

    if len(records) > 1:

        st.markdown(
            "### Revision History"
        )

        for record in records:

            st.markdown(
                f"""
                **Revision {getattr(record, "revision", 0)}**  
                Status: `{getattr(record, "status", "unknown")}`  
                {getattr(record, "output_summary", "")}
                """
            )
