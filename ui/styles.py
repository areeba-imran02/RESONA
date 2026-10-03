"""
RESONA - UI Styles

Centralized premium dark-theme styling for the Streamlit
application.
"""

import streamlit as st


def inject_styles() -> None:
    """
    Inject the main RESONA application theme.
    """

    st.markdown(
        """
        <style>
        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap'
        );

        :root {
            --resona-bg: #070b14;
            --resona-surface: #0d1422;
            --resona-surface-2: #111b2d;
            --resona-border: rgba(148, 163, 184, 0.14);
            --resona-text: #f8fafc;
            --resona-muted: #94a3b8;
            --resona-primary: #38bdf8;
            --resona-secondary: #818cf8;
            --resona-success: #34d399;
            --resona-warning: #fbbf24;
            --resona-danger: #fb7185;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 10% 10%,
                    rgba(56, 189, 248, 0.08),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 90% 15%,
                    rgba(129, 140, 248, 0.08),
                    transparent 30%
                ),
                var(--resona-bg);
            color: var(--resona-text);
            font-family: 'Inter', sans-serif;
        }

        .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: -0.03em;
        }

        .resona-logo {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: -0.07em;
            background: linear-gradient(
                135deg,
                #f8fafc 15%,
                #38bdf8 55%,
                #818cf8 100%
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 12px 35px rgba(56, 189, 248, 0.15);
        }

        .resona-tagline {
            color: var(--resona-muted);
            font-size: 0.95rem;
            margin-top: -0.35rem;
        }

        .hero {
            padding: 5rem 1rem 3rem 1rem;
            text-align: center;
        }

        .hero-badge {
            display: inline-block;
            padding: 0.45rem 0.9rem;
            border: 1px solid var(--resona-border);
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.65);
            color: #cbd5e1;
            font-size: 0.78rem;
            font-weight: 600;
            margin-bottom: 1.2rem;
        }

        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(2.6rem, 6vw, 5.4rem);
            line-height: 0.98;
            font-weight: 800;
            letter-spacing: -0.07em;
            margin: 0;
            background: linear-gradient(
                135deg,
                #ffffff 10%,
                #dbeafe 45%,
                #7dd3fc 72%,
                #a5b4fc 100%
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-description {
            max-width: 760px;
            margin: 1.5rem auto 2rem auto;
            color: #94a3b8;
            font-size: 1.05rem;
            line-height: 1.8;
        }

        .feature-card {
            min-height: 185px;
            padding: 1.5rem;
            border-radius: 18px;
            border: 1px solid var(--resona-border);
            background: linear-gradient(
                145deg,
                rgba(17, 27, 45, 0.94),
                rgba(10, 16, 29, 0.94)
            );
            box-shadow:
                0 20px 50px rgba(0, 0, 0, 0.18);
        }

        .feature-icon {
            font-size: 1.4rem;
            margin-bottom: 0.8rem;
        }

        .feature-title {
            color: #f8fafc;
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.45rem;
        }

        .feature-text {
            color: #94a3b8;
            font-size: 0.86rem;
            line-height: 1.65;
        }

        .section-label {
            color: #64748b;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
        }

        .metric-card {
            padding: 1.2rem;
            border-radius: 16px;
            border: 1px solid var(--resona-border);
            background: rgba(13, 20, 34, 0.86);
        }

        .metric-label {
            color: #64748b;
            font-size: 0.76rem;
            font-weight: 600;
        }

        .metric-value {
            color: #f8fafc;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 0.25rem;
        }

        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 7px;
            background: var(--resona-success);
            box-shadow: 0 0 12px rgba(52, 211, 153, 0.55);
        }

        .agent-card {
            padding: 1rem 1.15rem;
            border: 1px solid var(--resona-border);
            border-radius: 14px;
            background: rgba(13, 20, 34, 0.78);
            margin-bottom: 0.7rem;
        }

        .agent-name {
            color: #f8fafc;
            font-weight: 600;
            font-size: 0.9rem;
        }

        .agent-status {
            color: #64748b;
            font-size: 0.76rem;
        }

        .workflow-line {
            border-left: 1px solid rgba(56, 189, 248, 0.25);
            margin-left: 0.6rem;
            padding-left: 1.4rem;
        }

        .info-panel {
            padding: 1.4rem;
            border: 1px solid var(--resona-border);
            border-radius: 16px;
            background: rgba(13, 20, 34, 0.8);
        }

        div[data-testid="stSidebar"] {
            background: #080d18;
            border-right: 1px solid var(--resona-border);
        }

        div[data-testid="stSidebar"] .stButton button {
            text-align: left;
        }

        .stButton > button {
            border-radius: 10px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            min-height: 42px;
            font-weight: 600;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] > div {
            background: rgba(15, 23, 42, 0.75);
            border-color: var(--resona-border);
            color: #f8fafc;
        }

        .stProgress > div > div {
            background: linear-gradient(
                90deg,
                #38bdf8,
                #818cf8
            );
        }

        footer {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
