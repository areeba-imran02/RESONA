"""
RESONA - Agent Workflow UI

Displays the seven-agent emergency analysis pipeline
and the results returned by the orchestration layer.
"""

from typing import Any, Dict, List

import streamlit as st


AGENT_PIPELINE = [
    (
        "Situation Intelligence",
        "Understands the emergency and affected areas.",
    ),
    (
        "Needs Assessment",
        "Identifies humanitarian and operational needs.",
    ),
    (
        "Resource Intelligence",
        "Compares needs with available resources.",
    ),
    (
        "Logistics & Deployment",
        "Analyzes movement and accessibility constraints.",
    ),
    (
        "Priority & Impact",
        "Analyzes response priority factors.",
    ),
    (
        "Critic & Conflict Resolution",
        "Reviews findings and detects conflicts.",
    ),
    (
        "Response Coordinator",
        "Creates the coordinated response plan.",
    ),
]


def _build_context(
    emergency: Dict[str, Any],
) -> str:
    """
    Convert emergency form data into agent-readable context.
    """

    lines = [
        f"Emergency Type: {emergency.get('emergency_type')}",
        f"Severity: {emergency.get('severity')}",
        f"Location: {emergency.get('location')}",
        (
            "Affected Population: "
            f"{emergency.get('affected_population', 0)}"
        ),
        "",
        "Description:",
        emergency.get(
            "description",
            "",
        ),
        "",
        "Available Resources:",
    ]

    for resource in emergency.get(
        "resources",
        [],
    ):
        lines.append(
            (
                f"- {resource['name']}: "
                f"{resource['quantity']} "
                f"({resource['category']})"
            )
        )

    additional = emergency.get(
        "additional_information",
        "",
    )

    if additional:
        lines.extend(
            [
                "",
                "Additional Information:",
                additional,
            ]
        )

    return "\n".join(lines)


def _render_pipeline(
    completed_count: int = 0,
    running_index: int = -1,
) -> None:
    """
    Render the visual agent pipeline.
    """

    for index, (
        name,
        description,
    ) in enumerate(AGENT_PIPELINE):

        if index < completed_count:
            status = "Completed"
            symbol = "✓"

        elif index == running_index:
            status = "Processing"
            symbol = "●"

        else:
            status = "Waiting"
            symbol = "○"

        st.markdown(
            f"""
            <div class="agent-card">
                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:1rem;
                ">
                    <div>
                        <div class="agent-name">
                            {symbol}&nbsp; {index + 1:02d}
                            &nbsp; {name}
                        </div>

                        <div class="agent-status">
                            {description}
                        </div>
                    </div>

                    <div style="
                        color:#64748b;
                        font-size:0.75rem;
                    ">
                        {status}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_agent_workflow() -> None:
    """
    Render the agent workflow screen.
    """

    st.markdown(
        """
        <div class="section-label">
            MULTI-AGENT ORCHESTRATION
        </div>

        <h1 style="margin-top:0;">
            Agent Workflow
        </h1>

        <p style="color:#94a3b8;">
            Seven specialized agents collaborate to transform
            emergency information into a coordinated response.
        </p>
        """,
        unsafe_allow_html=True,
    )

    emergency = st.session_state.get(
        "pending_emergency"
    )

    if not emergency:
        st.info(
            "No emergency is currently queued. "
            "Create an emergency first."
        )

        if st.button(
            "Create Emergency",
            type="primary",
        ):
            st.session_state[
                "active_page"
            ] = "New Emergency"
            st.rerun()

        return

    st.markdown(
        "### Emergency Context"
    )

    st.markdown(
        f"""
        <div class="info-panel">
            <strong>
                {emergency.get('emergency_type')}
            </strong>
            <br>
            <span style="color:#94a3b8;">
                {emergency.get('location')}
                &nbsp; • &nbsp;
                {emergency.get('severity')}
                &nbsp; • &nbsp;
                {emergency.get('affected_population', 0):,}
                affected
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if "workflow_result" not in st.session_state:

        st.markdown(
            "### Ready for Analysis"
        )

        st.markdown(
            """
            <div class="info-panel">
                <p style="
                    color:#94a3b8;
                    line-height:1.7;
                    margin-bottom:0;
                ">
                    RESONA will pass the emergency context through
                    Situation Intelligence, Needs Assessment,
                    Resource Intelligence, Logistics, Priority,
                    Critic, and finally the Response Coordinator.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Run RESONA Analysis",
            type="primary",
            use_container_width=True,
        ):
            context = _build_context(
                emergency
            )

            st.session_state[
                "workflow_context"
            ] = context

            st.session_state[
                "run_workflow"
            ] = True

            st.rerun()

        return

    result = st.session_state[
        "workflow_result"
    ]

    if not result.get(
        "success",
        False,
    ):
        st.error(
            "The RESONA workflow could not complete."
        )

        error = result.get(
            "error",
            "Unknown workflow error.",
        )

        st.code(
            error,
            language="text",
        )

        if st.button(
            "Retry Analysis",
            type="primary",
        ):
            st.session_state.pop(
                "workflow_result",
                None,
            )
            st.session_state[
                "run_workflow"
            ] = True
            st.rerun()

        return

    state = result.get(
        "state",
        {},
    ) or {}

    history = state.get(
        "agent_history",
        [],
    ) or []

    completed_agents = sum(
        1
        for record in history
        if record.get("status") == "completed"
    )

    st.markdown(
        "### Execution Pipeline"
    )

    _render_pipeline(
        completed_count=min(
            completed_agents,
            len(AGENT_PIPELINE),
        )
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.success(
        "RESONA multi-agent workflow completed."
    )

    st.markdown(
        "### Agent Execution Records"
    )

    for record in history:

        with st.expander(
            record.get(
                "agent_name",
                "Agent",
            )
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    "**Status:**",
                    record.get(
                        "status",
                        "unknown",
                    ),
                )

                st.write(
                    "**Revision:**",
                    record.get(
                        "revision",
                        0,
                    ),
                )

            with col2:
                st.write(
                    "**Upstream:**",
                    ", ".join(
                        record.get(
                            "upstream_agents",
                            [],
                        )
                    ) or "None",
                )

                st.write(
                    "**Downstream:**",
                    ", ".join(
                        record.get(
                            "downstream_agents",
                            [],
                        )
                    ) or "None",
                )

            output = record.get(
                "output_summary",
                "",
            )

            if output:
                st.markdown(
                    "**Output Summary**"
                )
                st.write(output)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "View Final Response",
        type="primary",
        use_container_width=True,
    ):
        st.session_state[
            "active_page"
        ] = "Dashboard"
        st.rerun()
