"""
RESONA - Resources View

Displays available emergency resources, constraints,
shortages, and resource intelligence from the workflow.
"""

from typing import Any, Dict, List

import pandas as pd
import streamlit as st


def _get_state() -> Dict[str, Any]:
    """
    Return the current workflow state.
    """

    result = st.session_state.get(
        "workflow_result",
        {},
    )

    return result.get(
        "state",
        {},
    ) or {}


def render_resources() -> None:
    """
    Render the resource intelligence interface.
    """

    st.markdown(
        """
        <div class="section-label">
            RESOURCE INTELLIGENCE
        </div>

        <h1 style="margin-top:0;">
            Resources
        </h1>

        <p style="color:#94a3b8;">
            Monitor available resources, identified gaps,
            constrained supplies, and allocation information.
        </p>
        """,
        unsafe_allow_html=True,
    )

    state = _get_state()

    resources = state.get(
        "resources",
        {},
    ) or {}

    available = resources.get(
        "available_resources",
        [],
    ) or []

    gaps = resources.get(
        "resource_gaps",
        [],
    ) or []

    constrained = resources.get(
        "constrained_resources",
        [],
    ) or []

    surplus = resources.get(
        "surplus_resources",
        [],
    ) or []

    columns = st.columns(4)

    metrics = [
        (
            "Available Resources",
            len(available),
        ),
        (
            "Resource Gaps",
            len(gaps),
        ),
        (
            "Constrained",
            len(constrained),
        ),
        (
            "Surplus",
            len(surplus),
        ),
    ]

    for column, (
        label,
        value,
    ) in zip(
        columns,
        metrics,
    ):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        {label}
                    </div>
                    <div class="metric-value">
                        {value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    if available:

        st.markdown(
            "### Available Resources"
        )

        rows = []

        for resource in available:
            rows.append(
                {
                    "Resource": resource.get(
                        "name",
                        "Unknown",
                    ),
                    "Category": resource.get(
                        "category",
                        "Unknown",
                    ),
                    "Quantity": resource.get(
                        "quantity",
                        0,
                    ),
                    "Unit": resource.get(
                        "unit",
                        "",
                    ),
                    "Location": resource.get(
                        "location",
                        "",
                    ),
                }
            )

        dataframe = pd.DataFrame(
            rows
        )

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "No structured resource information is available yet."
        )

    if gaps:

        st.markdown(
            "### Resource Gaps"
        )

        for gap in gaps:

            resource_name = gap.get(
                "resource",
                "Unknown resource",
            )

            explanation = gap.get(
                "explanation",
                "",
            )

            severity = gap.get(
                "severity",
                "medium",
            )

            st.markdown(
                f"""
                <div class="agent-card">
                    <div class="agent-name">
                        {resource_name}
                    </div>

                    <div class="agent-status">
                        Severity: {severity}
                    </div>

                    <p style="
                        color:#94a3b8;
                        margin-bottom:0;
                    ">
                        {explanation}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if constrained:

        st.markdown(
            "### Constrained Resources"
        )

        for resource in constrained:
            st.markdown(
                f"- {resource}"
            )

    if surplus:

        st.markdown(
            "### Surplus Resources"
        )

        for resource in surplus:
            st.markdown(
                f"- {resource}"
            )

    allocation_constraints = resources.get(
        "allocation_constraints",
        [],
    ) or []

    if allocation_constraints:

        st.markdown(
            "### Allocation Constraints"
        )

        for constraint in allocation_constraints:
            st.warning(
                constraint
            )
