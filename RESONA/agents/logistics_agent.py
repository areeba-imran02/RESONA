"""
RESONA - Logistics & Deployment Agent

Analyzes accessibility, transportation, deployment constraints,
and operational logistics for emergency response.
"""

from crewai import Agent, LLM

from config.settings import (
    AGENT_TEMPERATURE,
    get_groq_api_key,
    get_groq_model,
)


def create_logistics_agent() -> Agent:
    """
    Create and return the Logistics & Deployment Agent.
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
        role="Emergency Logistics and Deployment Specialist",

        goal=(
            "Develop practical logistics and deployment strategies "
            "for an emergency response. Analyze area accessibility, "
            "transportation capacity, vehicle availability, travel "
            "constraints, volunteer deployment, medical team "
            "deployment, and resource movement requirements. "
            "Identify operational bottlenecks and propose feasible "
            "deployment options without inventing unavailable "
            "transport or infrastructure."
        ),

        backstory=(
            "You are the Logistics and Deployment Agent in RESONA. "
            "You specialize in turning resource availability and "
            "emergency needs into practical field deployment plans. "
            "You consider road accessibility, transportation limits, "
            "distance or movement constraints when provided, vehicle "
            "capacity, volunteer availability, medical team deployment, "
            "and delivery sequencing. You understand that a resource "
            "cannot simply be allocated on paper if it cannot physically "
            "reach the affected area."
        ),

        llm=llm,

        verbose=False,

        allow_delegation=False,

        max_iter=5,
    )
