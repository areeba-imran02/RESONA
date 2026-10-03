"""
RESONA - Memory Intelligence UI

Displays RESONA's short-term workflow memory and
long-term SQLite memory.
"""

import streamlit as st

from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.database import ResonaDatabase


def render_memory_view():

    st.markdown(
        """
        <div class="page-header">
            <div class="page-eyebrow">
                CONTEXT & MEMORY
            </div>
            <h1>Memory</h1>
            <p>
                RESONA maintains current workflow context
                and persistent emergency-response knowledge.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    short_term = ShortTermMemory()

    database = ResonaDatabase()

    long_term = LongTermMemory(
        database=database
    )

    tab1, tab2 = st.tabs(
        [
            "Short-Term Memory",
            "Long-Term Memory",
        ]
    )

    # ========================================================
    # SHORT TERM
    # ========================================================

    with tab1:

        st.markdown(
            "### Current Workflow Context"
        )

        snapshot = short_term.snapshot()

        if not snapshot:

            st.info(
                "No active short-term memory is available."
            )

        else:

            status = snapshot.get(
                "status",
                snapshot.get(
                    "workflow_status",
                    "unknown",
                ),
            )

            revision_count = snapshot.get(
                "revision_count",
                0,
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Workflow Status",
                    str(status).title(),
                )

            with col2:
                st.metric(
                    "Revisions",
                    revision_count,
                )

            st.markdown(
                "#### Stored Context"
            )

            context = snapshot.get(
                "context",
                {},
            )

            if context:

                for key, value in context.items():

                    with st.expander(
                        str(key).replace(
                            "_",
                            " "
                        ).title()
                    ):
                        st.write(value)

            else:

                st.caption(
                    "No contextual data stored."
                )

            st.markdown(
                "#### Agent Outputs"
            )

            outputs = snapshot.get(
                "agent_outputs",
                {},
            )

            if outputs:

                for agent_name, output in outputs.items():

                    with st.expander(
                        agent_name
                    ):
                        st.write(output)

            else:

                st.caption(
                    "No agent outputs stored."
                )

    # ========================================================
    # LONG TERM
    # ========================================================

    with tab2:

        st.markdown(
            "### Persistent Response Memory"
        )

        try:

            summary = long_term.summary()

            if isinstance(summary, dict):

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Emergencies",
                        summary.get(
                            "emergencies",
                            0,
                        ),
                    )

                with col2:
                    st.metric(
                        "Identities",
                        summary.get(
                            "identities",
                            0,
                        ),
                    )

                with col3:
                    st.metric(
                        "Memory Records",
                        summary.get(
                            "memory_records",
                            0,
                        ),
                    )

            else:

                st.info(
                    "Long-term memory is available."
                )

        except Exception as exc:

            st.warning(
                f"Memory summary could not be loaded: {exc}"
            )

        st.markdown("---")

        st.markdown(
            "### Previous Emergencies"
        )

        try:

            history = (
                long_term.get_emergency_history()
            )

            if history:

                for emergency in history:

                    emergency_id = emergency.get(
                        "emergency_id",
                        "Unknown",
                    )

                    with st.expander(
                        str(emergency_id)
                    ):

                        st.write(
                            emergency
                        )

            else:

                st.caption(
                    "No previous emergencies stored yet."
                )

        except Exception as exc:

            st.warning(
                f"Emergency history could not be loaded: {exc}"
            )

        st.markdown("---")

        st.caption(
            "Long-term memory is stored locally in "
            "RESONA's SQLite database."
        )
