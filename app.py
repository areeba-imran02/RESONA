import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="RESONA | Emergency Response Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SESSION STATE
# ============================================================

if "launched" not in st.session_state:
    st.session_state.launched = False


# ============================================================
# GLOBAL STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap'
    );

    :root {
        --bg: #070a12;
        --panel: #0d1220;
        --panel-soft: #111827;
        --text: #f4f7fb;
        --muted: #8d98aa;
        --line: rgba(255,255,255,0.08);

        --violet: #8b5cf6;
        --cyan: #22d3ee;
        --blue: #3b82f6;

        --success: #34d399;
        --warning: #fbbf24;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 15% 10%,
                rgba(139, 92, 246, 0.12),
                transparent 28%
            ),
            radial-gradient(
                circle at 85% 20%,
                rgba(34, 211, 238, 0.08),
                transparent 26%
            ),
            linear-gradient(
                135deg,
                #05070d 0%,
                #080b14 48%,
                #060911 100%
            );

        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    footer {
        visibility: hidden;
    }


    /* ========================================================
       HIDE DEFAULT STREAMLIT ELEMENTS
       ======================================================== */

    [data-testid="stToolbar"] {
        display: none;
    }

    [data-testid="stDecoration"] {
        display: none;
    }


    /* ========================================================
       LANDING NAV
       ======================================================== */

    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.4rem 0 1.5rem 0;
        border-bottom: 1px solid var(--line);
    }

    .nav-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-mark {
        width: 38px;
        height: 38px;
        border-radius: 12px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 18px;
        font-weight: 800;

        color: white;

        background:
            linear-gradient(
                135deg,
                rgba(139, 92, 246, 0.95),
                rgba(34, 211, 238, 0.85)
            );

        box-shadow:
            0 0 28px rgba(139, 92, 246, 0.25);
    }

    .nav-name {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        letter-spacing: 0.08em;
    }

    .nav-status {
        color: #a9b4c5;
        font-size: 0.78rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 12px rgba(52, 211, 153, 0.7);
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero {
        text-align: center;
        padding: 6.5rem 1rem 4rem 1rem;
        position: relative;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;

        padding: 8px 14px;

        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 999px;

        background: rgba(139, 92, 246, 0.07);

        color: #c4b5fd;

        font-size: 0.76rem;
        font-weight: 600;

        letter-spacing: 0.08em;
        text-transform: uppercase;

        margin-bottom: 1.7rem;
    }


    /* ========================================================
       3D WORDMARK
       ======================================================== */

    .resona-logo {
        font-family: 'Space Grotesk', sans-serif;

        font-size: clamp(4rem, 11vw, 8.8rem);

        line-height: 0.95;

        font-weight: 800;

        letter-spacing: -0.075em;

        margin: 0;

        color: transparent;

        background:
            linear-gradient(
                105deg,
                #ffffff 5%,
                #c4b5fd 32%,
                #8b5cf6 58%,
                #22d3ee 92%
            );

        -webkit-background-clip: text;
        background-clip: text;

        position: relative;

        text-shadow:
            0 1px 0 rgba(255,255,255,0.15),
            0 6px 0 rgba(79, 52, 145, 0.18),
            0 12px 30px rgba(139,92,246,0.18);
    }

    .resona-submark {
        margin-top: 0.8rem;

        font-family: 'Space Grotesk', sans-serif;

        font-size: clamp(1rem, 2vw, 1.3rem);

        font-weight: 600;

        color: #dce4f2;

        letter-spacing: 0.04em;
    }

    .hero-description {
        max-width: 700px;
        margin: 1.4rem auto 0 auto;

        color: var(--muted);

        font-size: 1rem;
        line-height: 1.8;
    }


    /* ========================================================
       FEATURE STRIP
       ======================================================== */

    .feature-strip {
        display: grid;
        grid-template-columns:
            repeat(4, minmax(0, 1fr));

        gap: 12px;

        max-width: 1050px;

        margin: 3rem auto 2rem auto;
    }

    .feature-card {
        min-height: 125px;

        padding: 1.25rem;

        border-radius: 18px;

        border: 1px solid var(--line);

        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.045),
                rgba(255,255,255,0.015)
            );

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.03);

        text-align: left;
    }

    .feature-icon {
        width: 34px;
        height: 34px;

        border-radius: 10px;

        display: flex;
        align-items: center;
        justify-content: center;

        background:
            linear-gradient(
                135deg,
                rgba(139,92,246,0.18),
                rgba(34,211,238,0.10)
            );

        border: 1px solid rgba(139,92,246,0.18);

        margin-bottom: 0.8rem;

        color: #ddd6fe;
    }

    .feature-title {
        font-weight: 700;
        font-size: 0.88rem;
        margin-bottom: 0.35rem;
    }

    .feature-text {
        color: #7f8a9e;
        font-size: 0.74rem;
        line-height: 1.55;
    }


    /* ========================================================
       LAUNCH AREA
       ======================================================== */

    .launch-copy {
        text-align: center;

        color: #7f8a9e;

        font-size: 0.78rem;

        margin-top: 1.2rem;
    }


    /* ========================================================
       DASHBOARD
       ======================================================== */

    .dashboard-header {
        padding: 1rem 0 2rem 0;
    }

    .dashboard-kicker {
        color: #8b5cf6;

        font-size: 0.72rem;

        font-weight: 700;

        text-transform: uppercase;

        letter-spacing: 0.12em;

        margin-bottom: 0.5rem;
    }

    .dashboard-title {
        font-family: 'Space Grotesk', sans-serif;

        font-size: 2rem;

        font-weight: 700;

        letter-spacing: -0.04em;
    }

    .dashboard-subtitle {
        color: var(--muted);

        margin-top: 0.4rem;

        font-size: 0.88rem;
    }


    /* ========================================================
       METRIC CARDS
       ======================================================== */

    .metric-grid {
        display: grid;

        grid-template-columns:
            repeat(4, minmax(0, 1fr));

        gap: 14px;

        margin-bottom: 1.5rem;
    }

    .metric-card {
        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.055),
                rgba(255,255,255,0.018)
            );

        border: 1px solid var(--line);

        border-radius: 18px;

        padding: 1.25rem;

        min-height: 125px;
    }

    .metric-label {
        color: #7f8a9e;

        font-size: 0.72rem;

        text-transform: uppercase;

        letter-spacing: 0.08em;

        font-weight: 600;
    }

    .metric-value {
        font-family: 'Space Grotesk', sans-serif;

        font-size: 1.8rem;

        font-weight: 700;

        margin-top: 0.65rem;
    }

    .metric-detail {
        color: #657084;

        font-size: 0.72rem;

        margin-top: 0.25rem;
    }


    /* ========================================================
       SECTION CARDS
       ======================================================== */

    .section-card {
        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.04),
                rgba(255,255,255,0.015)
            );

        border: 1px solid var(--line);

        border-radius: 20px;

        padding: 1.4rem;

        min-height: 200px;
    }

    .section-title {
        font-family: 'Space Grotesk', sans-serif;

        font-size: 1rem;

        font-weight: 700;

        margin-bottom: 0.4rem;
    }

    .section-description {
        color: #788397;

        font-size: 0.78rem;

        line-height: 1.6;
    }


    /* ========================================================
       AGENT STATUS
       ======================================================== */

    .agent-row {
        display: flex;

        justify-content: space-between;

        align-items: center;

        padding: 0.75rem 0;

        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .agent-row:last-child {
        border-bottom: none;
    }

    .agent-name {
        font-size: 0.8rem;

        font-weight: 600;
    }

    .agent-status {
        font-size: 0.68rem;

        color: #64748b;

        display: flex;

        align-items: center;

        gap: 6px;
    }

    .waiting-dot {
        width: 6px;
        height: 6px;

        border-radius: 50%;

        background: #64748b;
    }


    /* ========================================================
       STREAMLIT BUTTONS
       ======================================================== */

    .stButton > button {

        width: 100%;

        min-height: 46px;

        border-radius: 12px;

        border: 1px solid rgba(139,92,246,0.35);

        background:
            linear-gradient(
                135deg,
                #7c3aed,
                #2563eb
            );

        color: white;

        font-family: 'Inter', sans-serif;

        font-weight: 700;

        font-size: 0.85rem;

        letter-spacing: 0.01em;

        box-shadow:
            0 10px 35px rgba(79,70,229,0.18);

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease,
            border-color 0.2s ease;
    }

    .stButton > button:hover {

        transform: translateY(-1px);

        border-color: rgba(34,211,238,0.5);

        box-shadow:
            0 14px 40px rgba(79,70,229,0.27);
    }


    /* ========================================================
       SELECTBOX / INPUTS
       ======================================================== */

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    textarea {

        background-color:
            rgba(255,255,255,0.035) !important;

        border-color:
            rgba(255,255,255,0.09) !important;

        border-radius: 12px !important;

        color: white !important;
    }

    label {

        color: #aab4c4 !important;

        font-size: 0.76rem !important;

        font-weight: 600 !important;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #080b14,
                #060810
            );

        border-right:
            1px solid rgba(255,255,255,0.06);
    }


    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media (max-width: 900px) {

        .feature-strip,
        .metric-grid {

            grid-template-columns:
                repeat(2, minmax(0, 1fr));
        }

        .hero {
            padding-top: 4rem;
        }
    }

    @media (max-width: 600px) {

        .feature-strip,
        .metric-grid {

            grid-template-columns: 1fr;
        }

        .hero {
            padding-top: 3rem;
        }

        .resona-logo {
            font-size: 4rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LANDING PAGE
# ============================================================

def render_landing():

    st.markdown(
        """
        <div class="top-nav">
            <div class="nav-brand">
                <div class="brand-mark">R</div>
                <div class="nav-name">RESONA</div>
            </div>

            <div class="nav-status">
                <span class="status-dot"></span>
                Intelligence Core Ready
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero">

            <div class="hero-badge">
                ◈ Multi-Agent Emergency Intelligence
            </div>

            <div class="resona-logo">
                RESONA
            </div>

            <div class="resona-submark">
                AI-Powered Emergency Response Intelligence
            </div>

            <div class="hero-description">
                A collaborative multi-agent platform that analyzes emergency
                situations, understands human needs, coordinates limited
                resources, resolves conflicting recommendations, and generates
                actionable response plans.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feature cards
    st.markdown(
        """
        <div class="feature-strip">

            <div class="feature-card">
                <div class="feature-icon">◎</div>
                <div class="feature-title">
                    Multi-Agent Intelligence
                </div>
                <div class="feature-text">
                    Specialized agents collaborate across situation,
                    needs, resources, logistics and priority analysis.
                </div>
            </div>

            <div class="feature-card">
                <div class="feature-icon">◇</div>
                <div class="feature-title">
                    Resource Coordination
                </div>
                <div class="feature-text">
                    Understand shortages, available capacity and
                    deployment constraints.
                </div>
            </div>

            <div class="feature-card">
                <div class="feature-icon">↻</div>
                <div class="feature-title">
                    Conflict Resolution
                </div>
                <div class="feature-text">
                    A dedicated critic agent reviews recommendations
                    and triggers re-evaluation when required.
                </div>
            </div>

            <div class="feature-card">
                <div class="feature-icon">◌</div>
                <div class="feature-title">
                    Context & Memory
                </div>
                <div class="feature-text">
                    Maintain current incident context and useful
                    historical operational information.
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # Launch button
    left, center, right = st.columns([1.2, 1, 1.2])

    with center:
        if st.button(
            "Launch RESONA  →",
            use_container_width=True,
        ):
            st.session_state.launched = True
            st.rerun()

    st.markdown(
        """
        <div class="launch-copy">
            Built for coordinated decision support in complex emergency situations.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():

    # Sidebar
    with st.sidebar:

        st.markdown(
            """
            <div style="
                padding: 0.5rem 0 1.5rem 0;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.15rem;
                font-weight: 800;
                letter-spacing: 0.04em;
            ">
                RESONA
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("Emergency Intelligence Platform")

        st.divider()

        st.radio(
            "Navigation",
            [
                "Dashboard",
                "New Emergency",
                "Agent Workflow",
                "Resources",
                "People & Volunteers",
                "Memory",
                "Agent Inspector",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        st.caption("SYSTEM")

        st.markdown(
            """
            <div style="
                display:flex;
                align-items:center;
                gap:8px;
                color:#94a3b8;
                font-size:0.75rem;
            ">
                <span style="
                    width:7px;
                    height:7px;
                    border-radius:50%;
                    background:#34d399;
                    box-shadow:0 0 10px rgba(52,211,153,.7);
                "></span>
                Intelligence Core Online
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Header
    st.markdown(
        """
        <div class="dashboard-header">

            <div class="dashboard-kicker">
                Command Center
            </div>

            <div class="dashboard-title">
                Emergency Intelligence Dashboard
            </div>

            <div class="dashboard-subtitle">
                Monitor incidents, resources, agents and coordinated response activity.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # Metrics
    st.markdown(
        """
        <div class="metric-grid">

            <div class="metric-card">
                <div class="metric-label">
                    Active Incidents
                </div>

                <div class="metric-value">
                    0
                </div>

                <div class="metric-detail">
                    No active analysis
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-label">
                    People Affected
                </div>

                <div class="metric-value">
                    —
                </div>

                <div class="metric-detail">
                    Awaiting incident data
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-label">
                    Critical Areas
                </div>

                <div class="metric-value">
                    —
                </div>

                <div class="metric-detail">
                    Not evaluated
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-label">
                    Active Agents
                </div>

                <div class="metric-value">
                    7
                </div>

                <div class="metric-detail">
                    Ready for analysis
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main sections
    left, right = st.columns([1.25, 0.75], gap="medium")

    with left:

        st.markdown(
            """
            <div class="section-card">

                <div class="section-title">
                    Multi-Agent Operations
                </div>

                <div class="section-description">
                    RESONA's specialized agents are ready to analyze a new
                    emergency scenario.
                </div>

                <br>

                <div class="agent-row">
                    <div class="agent-name">
                        Situation Intelligence
                    </div>

                    <div class="agent-status">
                        <span class="waiting-dot"></span>
                        Waiting
                    </div>
                </div>

                <div class="agent-row">
                    <div class="agent-name">
                        Needs Assessment
                    </div>

                    <div class="agent-status">
                        <span class="waiting-dot"></span>
                        Waiting
                    </div>
                </div>

                <div class="agent-row">
                    <div class="agent-name">
                        Resource Intelligence
                    </div>

                    <div class="agent-status">
                        <span class="waiting-dot"></span>
                        Waiting
                    </div>
                </div>

                <div class="agent-row">
                    <div class="agent-name">
                        Logistics & Deployment
                    </div>

                    <div class="agent-status">
                        <span class="waiting-dot"></span>
                        Waiting
                    </div>
                </div>

                <div class="agent-row">
                    <div class="agent-name">
                        Priority & Impact
                    </div>

                    <div class="agent-status">
                        <span class="waiting-dot"></span>
                        Waiting
                    </div>
                </div>

                <div class="agent-row">
                    <div class="agent-name">
                        Critic & Conflict Resolution
                    </div>

                    <div class="agent-status">
                        <span class="waiting-dot"></span>
                        Waiting
                    </div>
                </div>

                <div class="agent-row">
                    <div class="agent-name">
                        Response Coordinator
                    </div>

                    <div class="agent-status">
                        <span class="waiting-dot"></span>
                        Waiting
                    </div>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        st.markdown(
            """
            <div class="section-card">

                <div class="section-title">
                    Start an Analysis
                </div>

                <div class="section-description">
                    Provide an emergency scenario and let the RESONA
                    multi-agent engine coordinate the analysis.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button(
            "＋  Create New Emergency",
            use_container_width=True,
        ):
            st.info(
                "Emergency intake will be connected in the next build step."
            )


# ============================================================
# APP ROUTER
# ============================================================

if st.session_state.launched:
    render_dashboard()
else:
    render_landing()
