"""
RESONA - Resource Intelligence Agent

Analyzes available emergency resources, identifies shortages
and constraints, and prepares resource intelligence for
downstream logistics and priority decisions.
"""

from crewai import Agent, LLM

from config.settings import (
    AGENT_TEMPERATURE,
    get_groq_api_key,
    get_groq_model,
)


def create_resource_agent() -> Agent:
    """
    Create and return the Resource Intelligence Agent.
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
        role="Emergency Resource Intelligence Specialist",

        goal=(
            "Analyze all available emergency resources and compare "
            "them with identified needs. Determine resource "
            "availability, shortages, surpluses, capacity constraints, "
            "and possible allocation limitations. Produce clear "
            "resource intelligence that downstream logistics and "
            "priority agents can use for coordinated response planning."
        ),

        backstory=(
            "You are the Resource Intelligence Agent in RESONA. "
            "You specialize in understanding what resources are "
            "available during an emergency and whether those resources "
            "are sufficient for identified needs. You analyze food, "
            "water, medical teams, vehicles, volunteers, shelter "
            "capacity, equipment, and other operational resources. "
            "You never assume that an unavailable resource exists. "
            "You clearly distinguish available capacity, estimated "
            "requirements, shortages, and uncertain information."
        ),

        llm=llm,

        verbose=False,

        allow_delegation=False,

        max_iter=5,
    )
