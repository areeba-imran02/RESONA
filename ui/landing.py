"""
RESONA - Landing Page

Premium introduction screen shown before entering
the emergency response workspace.
"""

import streamlit as st


def render_landing_page() -> None:
    """
    Render the RESONA landing page.
    """

    st.markdown(
        """
        <div class="hero">

            <div class="hero-badge">
                AI-POWERED EMERGENCY RESPONSE INTELLIGENCE
            </div>

            <h1 class="hero-title">
                Many Agents.<br>
                One Coordinated Response.
            </h1>

            <p class="hero-description">
                RESONA transforms fragmented emergency information
                into coordinated response intelligence through a
                team of specialized AI agents that analyze,
                challenge, re-evaluate, and coordinate decisions.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Enter RESONA",
        type="primary",
        use_container_width=False,
    ):
        st.session_state["launched"] = True
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-label">Core Intelligence</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(4)

    features = [
        (
            "◈",
            "Multi-Agent Intelligence",
            "Seven specialized agents analyze situation, needs, "
            "resources, logistics, priorities, conflicts, "
            "and coordination.",
        ),
        (
            "◇",
            "Resource Coordination",
            "Available resources are compared with operational "
            "needs and constraints before allocation decisions.",
        ),
        (
            "△",
            "Conflict Resolution",
            "A dedicated critic reviews competing recommendations "
            "and can trigger targeted re-evaluation.",
        ),
        (
            "◎",
            "Context & Memory",
            "Identity context, active workflow state, and "
            "historical response information support decisions.",
        ),
    ]

    for column, feature in zip(
        columns,
        features,
    ):
        icon, title, description = feature

        with column:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">
                        {title}
                    </div>
                    <div class="feature-text">
                        {description}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#64748b;
            font-size:0.78rem;
        ">
            RESONA • Emergency Response Intelligence Platform
        </div>
        """,
        unsafe_allow_html=True,
    )
