"""
RESONA - Agent Workflow UI

Displays the actual seven-agent execution pipeline,
workflow status, critic review, revisions, and final response.
"""

import streamlit as st


AGENTS = [
    {
        "name": "Situation Intelligence Agent",
        "short": "Situation",
        "icon": "◈",
        "description": "Understands the emergency, affected areas, severity, conditions and constraints.",
    },
    {
        "name": "Needs Assessment Agent",
        "short": "Needs",
        "icon": "◎",
        "description": "Identifies humanitarian needs, urgency and vulnerable groups.",
    },
    {
        "name": "Resource Intelligence Agent",
        "short": "Resources",
        "icon": "▣",
        "description": "Analyzes available resources, shortages and allocation constraints.",
    },
    {
        "name": "Logistics & Deployment Agent",
        "short": "Logistics",
        "icon": "◇",
        "description": "Analyzes transportation, accessibility and deployment feasibility.",
    },
    {
        "name": "Priority & Impact Agent",
        "short": "Priority",
        "icon": "◆",
        "description": "Determines response priorities using transparent impact factors.",
    },
    {
        "name": "Critic & Conflict Resolution Agent",
        "short": "Critic",
        "icon": "△",
        "description": "Challenges findings, detects conflicts and triggers re-evaluation.",
    },
    {
        "name": "Response Coordinator Agent",
        "short": "Coordinator",
        "icon": "✦",
        "description": "Synthesizes reviewed findings into the final coordinated response.",
    },
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


def _get_agent_record(history, agent_name):
    """
    Return the latest execution record for an agent.
    """

    matches = [
        record
        for record in history
        if getattr(record, "agent_name", "") == agent_name
    ]

    if not matches:
        return None

    return matches[-1]


def _status_for_agent(history, agent_name):
    record = _get_agent_record(history, agent_name)

    if record is None:
        return "pending"

    status = getattr(record, "status", "pending")

    if status in {"completed", "reviewed"}:
        return "completed"

    if status == "revised":
        return "revised"

    if status == "failed":
        return "failed"

    return status


def _status_badge(status):
    badges = {
        "completed": "✓ COMPLETED",
        "revised": "↻ REVISED",
        "failed": "× FAILED",
        "running": "● RUNNING",
        "pending": "○ PENDING",
    }

    return badges.get(
        status,
        status.upper(),
    )


def _render_agent_card(agent, status, index):
    status_class = status.lower()

    st.markdown(
        f"""
        <div class="resona-agent-card {status_class}">
            <div class="agent-card-top">
                <div class="agent-index">{index:02d}</div>
                <div class="agent-icon">{agent["icon"]}</div>
                <div class="agent-status {status_class}">
                    {_status_badge(status)}
                </div>
            </div>

            <div class="agent-card-title">
                {agent["name"]}
            </div>

            <div class="agent-card-description">
                {agent["description"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_execution_details(workflow_result):
    history = _get_history(workflow_result)

    if not history:
        st.info(
            "No agent execution has been recorded yet."
        )
        return

    st.markdown(
        "### Agent Execution Details"
    )

    for record in history:

        agent_name = getattr(
            record,
            "agent_name",
            "Unknown Agent",
        )

        status = getattr(
            record,
            "status",
            "unknown",
        )

        summary = getattr(
            record,
            "output_summary",
            "",
        )

        revision = getattr(
            record,
            "revision",
            0,
        )

        timestamp = getattr(
            record,
            "timestamp",
            None,
        )

        with st.expander(
            f"{agent_name}  ·  {_status_badge(status)}"
        ):

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Status**")
                st.write(status.title())

                st.markdown("**Revision**")
                st.write(revision)

            with col2:
                st.markdown("**Timestamp**")
                st.write(
                    timestamp or "Not available"
                )

            st.markdown("**Output Summary**")

            st.info(
                summary
                or "No summary available."
            )

            upstream = getattr(
                record,
                "upstream_agents",
                [],
            )

            downstream = getattr(
                record,
                "downstream_agents",
                [],
            )

            if upstream:
                st.markdown("**Upstream Agents**")
                st.write(", ".join(upstream))

            if downstream:
                st.markdown("**Downstream Agents**")
                st.write(", ".join(downstream))


def _render_critic_panel(workflow_result):
    state = _get_state(workflow_result)

    if not state:
        return

    critic = getattr(
        state,
        "critic",
        None,
    )

    if not critic:
        return

    st.markdown(
        "### Conflict & Review Layer"
    )

    conflicts = getattr(
        critic,
        "conflicts_detected",
        [],
    )

    requires_revision = getattr(
        critic,
        "requires_re_evaluation",
        False,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Conflicts",
            len(conflicts),
        )

    with col2:
        st.metric(
            "Re-evaluation",
            "Required"
            if requires_revision
            else "Not Required",
        )

    with col3:
        st.metric(
            "Revisions",
            getattr(
                state,
                "revision_count",
                0,
            ),
        )

    if conflicts:

        st.markdown(
            "#### Detected Conflicts"
        )

        for conflict in conflicts:

            severity = getattr(
                conflict,
                "severity",
                "medium",
            )

            description = getattr(
                conflict,
                "description",
                "Conflict detected.",
            )

            agents = getattr(
                conflict,
                "agents_involved",
                [],
            )

            st.warning(
                f"**{severity.upper()}** — {description}"
            )

            if agents:
                st.caption(
                    "Agents involved: "
                    + ", ".join(agents)
                )

    else:
        st.success(
            "No unresolved conflicts were identified "
            "by the critic."
        )

    re_eval_agents = getattr(
        critic,
        "agents_to_re_evaluate",
        [],
    )

    if re_eval_agents:

        st.markdown(
            "**Agents selected for re-evaluation:**"
        )

        st.write(
            ", ".join(re_eval_agents)
        )


def _render_final_response(workflow_result):
    state = _get_state(workflow_result)

    if not state:
        return

    response = getattr(
        state,
        "final_response",
        None,
    )

    if not response:
        return

    st.markdown(
        "### Final Coordinated Response"
    )

    st.markdown(
        f"""
        <div class="resona-final-panel">
            <div class="final-label">
                COORDINATED RESPONSE PLAN
            </div>
            <div class="final-summary">
                {response.emergency_summary}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("#### Priority Areas")

        priorities = getattr(
            response,
            "priority_areas",
            [],
        )

        if priorities:
            for priority in priorities:
                st.markdown(
                    f"• **{priority}**"
                )
        else:
            st.caption(
                "No priority areas returned."
            )

    with col2:

        st.markdown("#### Immediate Actions")

        actions = getattr(
            response,
            "immediate_actions",
            [],
        )

        if actions:
            for action in actions:
                st.markdown(
                    f"• {action}"
                )
        else:
            st.caption(
                "No immediate actions returned."
            )

    st.markdown(
        "#### Situation Assessment"
    )

    st.write(
        getattr(
            response,
            "situation_assessment",
            "No assessment available.",
        )
    )

    allocations = getattr(
        response,
        "resource_allocations",
        [],
    )

    if allocations:

        st.markdown(
            "#### Resource Allocations"
        )

        allocation_rows = []

        for allocation in allocations:
            allocation_rows.append(
                {
                    "Area": getattr(
                        allocation,
                        "area",
                        "",
                    ),
                    "Resource": getattr(
                        allocation,
                        "resource",
                        "",
                    ),
                    "Quantity": getattr(
                        allocation,
                        "quantity",
                        None,
                    ),
                    "Unit": getattr(
                        allocation,
                        "unit",
                        "",
                    ),
                    "Rationale": getattr(
                        allocation,
                        "rationale",
                        "",
                    ),
                }
            )

        st.dataframe(
            allocation_rows,
            use_container_width=True,
            hide_index=True,
        )

    deployments = getattr(
        response,
        "logistics_and_deployment",
        [],
    )

    if deployments:

        st.markdown(
            "#### Logistics & Deployment"
        )

        for deployment in deployments:

            area = getattr(
                deployment,
                "area",
                "Unknown area",
            )

            resource = getattr(
                deployment,
                "resource",
                "Unknown resource",
            )

            quantity = getattr(
                deployment,
                "recommended_quantity",
                None,
            )

            feasibility = getattr(
                deployment,
                "feasibility",
                "unknown",
            )

            st.markdown(
                f"""
                **{area}** — {resource}

                Recommended quantity: `{quantity}`  
                Feasibility: `{feasibility}`
                """
            )

    gaps = getattr(
        response,
        "information_gaps",
        [],
    )

    if gaps:

        st.markdown(
            "#### Information Gaps"
        )

        for gap in gaps:
            st.warning(gap)

    uncertainty = getattr(
        response,
        "uncertainty_notes",
        [],
    )

    if uncertainty:

        st.markdown(
            "#### Uncertainty Notes"
        )

        for note in uncertainty:
            st.caption(note)

    confidence = getattr(
        response,
        "confidence",
        "medium",
    )

    st.markdown(
        f"**Overall response confidence:** `{confidence}`"
    )


def render_agent_workflow(workflow_result=None):
    """
    Main Agent Workflow page.
    """

    st.markdown(
        """
        <div class="page-header">
            <div class="page-eyebrow">
                MULTI-AGENT ORCHESTRATION
            </div>

            <h1>Agent Workflow</h1>

            <p>
                Watch RESONA's specialized agents analyze,
                challenge, revise and coordinate the emergency
                response.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    emergency = st.session_state.get(
        "pending_emergency"
    )

    if not emergency:

        st.info(
            "Create an emergency scenario first "
            "to start the RESONA agent workflow."
        )

        if st.button(
            "＋ Create Emergency",
            type="primary",
        ):
            st.session_state["active_page"] = (
                "Create Emergency"
            )
            st.rerun()

        return

    # --------------------------------------------------------
    # Emergency summary
    # --------------------------------------------------------

    st.markdown(
        "### Active Emergency"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Emergency",
            emergency.get(
                "emergency_type",
                "Unknown",
            ),
        )

    with col2:
        st.metric(
            "Severity",
            emergency.get(
                "severity",
                "Unknown",
            ).title(),
        )

    with col3:
        population = emergency.get(
            "affected_population",
            0,
        )

        st.metric(
            "Affected",
            f"{population:,}",
        )

    with col4:
        st.metric(
            "Location",
            emergency.get(
                "location",
                "Unknown",
            ),
        )

    st.markdown("---")

    # --------------------------------------------------------
    # Agent pipeline
    # --------------------------------------------------------

    st.markdown(
        "### RESONA Agent Network"
    )

    history = _get_history(
        workflow_result
    )

    for index, agent in enumerate(
        AGENTS,
        start=1,
    ):

        status = _status_for_agent(
            history,
            agent["name"],
        )

        _render_agent_card(
            agent,
            status,
            index,
        )

        if index < len(AGENTS):
            st.markdown(
                '<div class="workflow-connector">↓</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # --------------------------------------------------------
    # Run button
    # --------------------------------------------------------

    if not workflow_result:

        st.markdown(
            """
            <div class="run-intro">
                <h3>Ready to analyze</h3>
                <p>
                    RESONA will run the complete multi-agent
                    emergency response workflow, including
                    independent analysis, conflict review,
                    conditional re-evaluation and final
                    coordination.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "▶  Run RESONA Analysis",
            type="primary",
            use_container_width=True,
        ):

            st.session_state["run_workflow"] = True
            st.rerun()

        return

    # --------------------------------------------------------
    # Workflow result status
    # --------------------------------------------------------

    success = workflow_result.get(
        "success",
        False,
    )

    if success:

        st.success(
            "RESONA analysis completed successfully."
        )

    else:

        st.error(
            workflow_result.get(
                "error",
                "The RESONA workflow could not be completed.",
            )
        )

        if st.button(
            "↻ Retry Analysis",
            type="primary",
        ):

            st.session_state["workflow_result"] = None
            st.session_state["run_workflow"] = True
            st.rerun()

        return

    # --------------------------------------------------------
    # Critic
    # --------------------------------------------------------

    _render_critic_panel(
        workflow_result
    )

    st.markdown("---")

    # --------------------------------------------------------
    # Execution details
    # --------------------------------------------------------

    _render_execution_details(
        workflow_result
    )

    st.markdown("---")

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    _render_final_response(
        workflow_result
    )
