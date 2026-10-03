"""
RESONA - Memory View

Displays active short-term workflow memory and selected
long-term emergency-response memory.
"""

from typing import Any, Dict

import streamlit as st

from memory.database import ResonaDatabase
from memory.long_term import LongTermMemory
from memory.short_term import ShortTermMemory


def render_memory_view() -> None:
    """
    Render RESONA memory information.
    """

    st.markdown(
        """
        <div class="section-label">
            CONTEXT & MEMORY
        </div>

        <h1 style="margin-top:0;">
            Memory
        </h1>

        <p style="color:#94a3b8;">
            RESONA maintains active workflow context and persistent
            operational history to support continuity across
            emergency-response sessions.
        </p>
        """,
        unsafe_allow_html=True,
    )

    short_term = ShortTermMemory()

    try:
        long_term = LongTermMemory(
            database=ResonaDatabase()
        )
    except Exception as exc:
        long_term = None
        st.warning(
            f"Long-term memory unavailable: {exc}"
        )

    tab1, tab2 = st.tabs(
        [
            "Short-Term Memory",
            "Long-Term Memory",
        ]
    )

    with tab1:

        st.markdown(
            "### Current Workflow State"
        )

        snapshot = short_term.snapshot()

        if not snapshot:
            st.info(
                "No active short-term memory is available."
            )
        else:
            status = snapshot.get(
                "workflow_status",
                "unknown",
            )

            revision = snapshot.get(
                "revision_count",
                0,
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Workflow Status",
                    status,
                )

            with col2:
                st.metric(
                    "Revisions",
                    revision,
                )

            contexts = snapshot.get(
                "context",
                {},
            )

            if contexts:
                st.markdown(
                    "### Active Context"
                )
                st.json(
                    contexts
                )

            conflicts = snapshot.get(
                "conflicts",
                [],
            )

            if conflicts:
                st.markdown(
                    "### Active Conflicts"
                )

                for conflict in conflicts:
                    st.warning(
                        str(conflict)
                    )

            decisions = snapshot.get(
                "decisions",
                [],
            )

            if decisions:
                st.markdown(
                    "### Decisions"
                )

                for decision in decisions:
                    st.markdown(
                        f"- {decision}"
                    )

    with tab2:

        if long_term is None:
            st.info(
                "Long-term memory is not available."
            )
            return

        st.markdown(
            "### Stored Emergency History"
        )

        try:
            emergencies = (
                long_term.get_emergency_history(
                    limit=10
                )
            )
        except Exception as exc:
            emergencies = []
            st.warning(
                f"Could not load emergency history: {exc}"
            )

        if not emergencies:
            st.info(
                "No previous emergency records are available."
            )
        else:

            for emergency in emergencies:

                emergency_id = emergency.get(
                    "emergency_id",
                    "Unknown",
                )

                emergency_type = emergency.get(
                    "emergency_type",
                    "Unknown",
                )

                location = emergency.get(
                    "location",
                    "Unknown",
                )

                status = emergency.get(
                    "status",
                    "Unknown",
                )

                with st.expander(
                    f"{emergency_id} — {emergency_type}"
                ):
                    st.write(
                        "**Location:**",
                        location,
                    )

                    st.write(
                        "**Status:**",
                        status,
                    )

                    st.write(
                        "**Created:**",
                        emergency.get(
                            "created_at",
                            "Unknown",
                        ),
                    )

        st.markdown(
            "### Memory Architecture"
        )

        st.markdown(
            """
            <div class="info-panel">

                <p>
                    <strong>Short-Term Memory</strong><br>
                    Current emergency context, agent outputs,
                    conflicts, revisions, decisions, and workflow
                    events.
                </p>

                <p>
                    <strong>Long-Term Memory</strong><br>
                    Previous emergency records, response plans,
                    identities, organizations, volunteers,
                    resources, and historical workflow information.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )
