"""
RESONA - Application Settings

Central configuration for:
- Groq API
- LLM model
- Application metadata
- Agent workflow limits
"""

import os
from typing import Optional

import streamlit as st


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "RESONA"
APP_TITLE = "RESONA — AI-Powered Emergency Response Intelligence Platform"

APP_TAGLINE = "Many Agents. One Coordinated Response."

APP_DESCRIPTION = (
    "RESONA transforms fragmented emergency information into "
    "coordinated response intelligence through collaborating AI agents."
)


# ============================================================
# GROQ CONFIGURATION
# ============================================================

GROQ_API_BASE = "https://api.groq.com/openai/v1"

DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Safely retrieve a configuration value.

    Priority:
    1. Streamlit secrets
    2. Environment variables
    3. Default value
    """

    # Try Streamlit secrets first
    try:
        value = st.secrets.get(name)

        if value:
            return str(value).strip()

    except Exception:
        pass

    # Fall back to environment variables
    value = os.getenv(name)

    if value:
        return value.strip()

    return default


def get_groq_api_key() -> Optional[str]:
    """
    Return the Groq API key from Streamlit secrets
    or environment variables.
    """

    return get_secret("GROQ_API_KEY")


def get_groq_model() -> str:
    """
    Return the configured Groq model.

    A custom GROQ_MODEL can be provided through
    Streamlit secrets or environment variables.
    """

    return get_secret(
        "GROQ_MODEL",
        DEFAULT_GROQ_MODEL,
    ) or DEFAULT_GROQ_MODEL


# ============================================================
# AGENT WORKFLOW CONFIGURATION
# ============================================================

MAX_AGENT_REVISIONS = 2

AGENT_TEMPERATURE = 0.2

AGENT_MAX_ITERATIONS = 5


# ============================================================
# MEMORY CONFIGURATION
# ============================================================

SHORT_TERM_MEMORY_ENABLED = True
LONG_TERM_MEMORY_ENABLED = True

DATABASE_FILE = "data/resona.db"


# ============================================================
# FILE / DOCUMENT CONFIGURATION
# ============================================================

SUPPORTED_DOCUMENT_TYPES = [
    "pdf",
    "txt",
    "csv",
    "xlsx",
]

MAX_UPLOAD_SIZE_MB = 10


# ============================================================
# APPLICATION LIMITS
# ============================================================

MAX_AFFECTED_POPULATION = 10_000_000

MAX_VOLUNTEERS = 100_000

MAX_RESOURCES = 100_000


# ============================================================
# HELPER
# ============================================================

def validate_configuration() -> tuple[bool, str]:
    """
    Validate the minimum configuration required
    before starting the multi-agent workflow.
    """

    api_key = get_groq_api_key()

    if not api_key:
        return (
            False,
            "GROQ_API_KEY is not configured. "
            "Add it to Streamlit Secrets before running RESONA.",
        )

    model = get_groq_model()

    if not model:
        return (
            False,
            "GROQ_MODEL is not configured.",
        )

    return True, "Configuration is valid."
