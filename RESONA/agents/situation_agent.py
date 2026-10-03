"""
RESONA - Situation Intelligence Agent

Responsible for understanding the emergency situation
before other agents make operational decisions.
"""

from crewai import Agent, LLM

from config.settings import (
    AGENT_TEMPERATURE,
    get_groq_api_key,
    get_groq_model,
)


def create_situation_agent() -> Agent:
    """
    Create and return the Situation Intelligence Agent.
    """

    api_key = get_groq_api_key()

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured. "
            "Add GROQ_API_KEY to Streamlit Secrets."
        )

    llm = LLM(
        model=f"groq/{get_groq_model()}",
        api_key=api_key,
        temperature=AGENT_TEMPERATURE,
    )

    return Agent(
        role="Situation Intelligence Specialist",

        goal=(
            "Build a clear, structured understanding of an emergency "
            "from the information provided, identify affected areas, "
            "severity, population impact, accessibility conditions, "
            "critical circumstances, missing information, and "
            "important operational constraints."
        ),

        backstory=(
            "You are the Situation Intelligence Agent in RESONA, "
            "an emergency response coordination platform. "
            "You specialize in turning fragmented emergency reports "
            "into structured situational intelligence. "
            "You carefully distinguish confirmed information from "
            "assumptions and unknowns. You never invent facts. "
            "Your assessment becomes an input for downstream "
            "needs, resource, logistics, and priority agents."
        ),

        llm=llm,

        verbose=False,

        allow_delegation=False,

        max_iter=5,
    )
