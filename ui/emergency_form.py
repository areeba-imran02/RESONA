"""
RESONA - Emergency Intake Form

Collects structured emergency information before
starting the multi-agent analysis.
"""

from typing import Any, Dict

import streamlit as st


EMERGENCY_TYPES = [
    "Flood",
    "Extreme Rainfall",
    "Earthquake",
    "Heatwave",
    "Large-Scale Fire",
    "Water Shortage",
    "Community Displacement",
    "Humanitarian Emergency",
    "Other",
]


def _resource_row(
    name: str,
    category: str,
    default: float = 0,
) -> Dict[str, Any]:
    """
    Build a resource record.
    """

    quantity = st.number_input(
        name,
        min_value=0.0,
        value=float(default),
        step=1.0,
        key=f"resource_{category}",
    )

    return {
        "name": name,
        "category": category,
        "quantity": quantity,
    }


def render_emergency_form() -> None:
    """
    Render the emergency intake interface.
    """

    st.markdown(
        """
        <div class="section-label">
            EMERGENCY INTAKE
        </div>

        <h1 style="margin-top:0;">
            Create Emergency
        </h1>

        <p style="
            color:#94a3b8;
            max-width:760px;
        ">
            Provide the available emergency information.
            RESONA's agents will analyze the information,
            identify gaps, compare resources, and coordinate
            a response plan.
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.form(
        "resona_emergency_form",
        clear_on_submit=False,
    ):

        st.markdown(
            "### Emergency Information"
        )

        col1, col2 = st.columns(2)

        with col1:
            emergency_type = st.selectbox(
                "Emergency Type",
                EMERGENCY_TYPES,
            )

        with col2:
            severity = st.selectbox(
                "Overall Severity",
                [
                    "Low",
                    "Moderate",
                    "High",
                    "Critical",
                    "Unknown",
                ],
                index=2,
            )

        location = st.text_input(
            "Location",
            placeholder=(
                "Example: Faisalabad, Punjab"
            ),
        )

        description = st.text_area(
            "Emergency Description",
            placeholder=(
                "Describe what happened, affected areas, "
                "current conditions, and important observations."
            ),
            height=130,
        )

        affected_population = st.number_input(
            "Estimated Affected Population",
            min_value=0,
            max_value=10_000_000,
            value=0,
            step=100,
        )

        st.markdown(
            "### Available Resources"
        )

        resource_columns = st.columns(2)

        with resource_columns[0]:

            food = _resource_row(
                "Food Kits",
                "food",
            )

            water = _resource_row(
                "Water Units",
                "water",
            )

            vehicles = _resource_row(
                "Emergency Vehicles",
                "transport",
            )

        with resource_columns[1]:

            volunteers = _resource_row(
                "Volunteers",
                "human_resources",
            )

            medical = _resource_row(
                "Medical Teams",
                "medical",
            )

            shelter = _resource_row(
                "Shelter Capacity",
                "shelter",
            )

        additional_information = st.text_area(
            "Additional Information",
            placeholder=(
                "Road conditions, urgent medical cases, "
                "vulnerable groups, shortages, etc."
            ),
            height=120,
        )

        submitted = st.form_submit_button(
            "Start Multi-Agent Analysis",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        if not location.strip():
            st.error(
                "Please provide the emergency location."
            )
            return

        if not description.strip():
            st.error(
                "Please provide a description of the emergency."
            )
            return

        resources = [
            food,
            water,
            vehicles,
            volunteers,
            medical,
            shelter,
        ]

        resources = [
            resource
            for resource in resources
            if resource["quantity"] > 0
        ]

        emergency_data = {
            "emergency_type": emergency_type,
            "severity": severity,
            "location": location.strip(),
            "description": description.strip(),
            "affected_population": (
                affected_population
            ),
            "resources": resources,
            "additional_information": (
                additional_information.strip()
            ),
        }

        st.session_state[
            "pending_emergency"
        ] = emergency_data

        st.session_state[
            "active_page"
        ] = "Agent Workflow"

        st.rerun()
