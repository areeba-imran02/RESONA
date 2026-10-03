"""
RESONA - Resource Intelligence UI
"""

import streamlit as st
import pandas as pd


def _get_state(workflow_result):
    if not workflow_result:
        return None

    return workflow_result.get("state")


def render_resources(workflow_result=None):

    st.markdown(
        """
        <div class="page-header">
            <div class="page-eyebrow">
                RESOURCE INTELLIGENCE
            </div>
            <h1>Resources</h1>
            <p>
                Monitor available resources, shortages,
                constraints and allocation intelligence.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    state = _get_state(workflow_result)

    if not state:

        st.info(
            "Run an emergency analysis to populate "
            "resource intelligence."
        )

        return

    resources = getattr(
        state,
        "resources",
        None,
    )

    if not resources:

        st.info(
            "Resource assessment is not available."
        )

        return

    available = getattr(
        resources,
        "available_resources",
        [],
    )

    gaps = getattr(
        resources,
        "resource_gaps",
        [],
    )

    constrained = getattr(
        resources,
        "constrained_resources",
        [],
    )

    surplus = getattr(
        resources,
        "surplus_resources",
        [],
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Resource Types",
            len(available),
        )

    with col2:
        st.metric(
            "Resource Gaps",
            len(gaps),
        )

    with col3:
        st.metric(
            "Constrained",
            len(constrained),
        )

    with col4:
        st.metric(
            "Surplus",
            len(surplus),
        )

    st.markdown("---")

    # --------------------------------------------------------
    # Available resources
    # --------------------------------------------------------

    st.markdown(
        "### Available Resources"
    )

    if available:

        rows = []

        for resource in available:

            rows.append(
                {
                    "Resource": getattr(
                        resource,
                        "name",
                        "",
                    ),
                    "Category": getattr(
                        resource,
                        "category",
                        "",
                    ),
                    "Quantity": getattr(
                        resource,
                        "quantity",
                        0,
                    ),
                    "Unit": getattr(
                        resource,
                        "unit",
                        "",
                    ),
                    "Location": getattr(
                        resource,
                        "location",
                        "",
                    ),
                    "Available": (
                        "Yes"
                        if getattr(
                            resource,
                            "available",
                            True,
                        )
                        else "No"
                    ),
                }
            )

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No available resources were identified."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # Resource gaps
    # --------------------------------------------------------

    st.markdown(
        "### Resource Gaps"
    )

    if gaps:

        for gap in gaps:

            resource_name = getattr(
                gap,
                "resource",
                "Unknown resource",
            )

            shortage = getattr(
                gap,
                "shortage_quantity",
                None,
            )

            area = getattr(
                gap,
                "affected_area",
                None,
            )

            severity = getattr(
                gap,
                "severity",
                "medium",
            )

            explanation = getattr(
                gap,
                "explanation",
                "",
            )

            location_text = (
                f" — {area}"
                if area
                else ""
            )

            st.warning(
                f"**{resource_name}{location_text}**  \n"
                f"Shortage: `{shortage}`  \n"
                f"Severity: `{severity}`  \n"
                f"{explanation}"
            )

    else:

        st.success(
            "No explicit resource shortages were identified."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # Constraints and surplus
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### Constrained Resources"
        )

        if constrained:

            for item in constrained:
                st.markdown(
                    f"• {item}"
                )

        else:

            st.caption(
                "No constrained resources reported."
            )

    with col2:

        st.markdown(
            "### Surplus Resources"
        )

        if surplus:

            for item in surplus:
                st.markdown(
                    f"• {item}"
                )

        else:

            st.caption(
                "No surplus resources reported."
            )

    allocation_constraints = getattr(
        resources,
        "allocation_constraints",
        [],
    )

    if allocation_constraints:

        st.markdown("---")

        st.markdown(
            "### Allocation Constraints"
        )

        for constraint in allocation_constraints:
            st.warning(constraint)
