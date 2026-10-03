"""
RESONA - Priority & Impact Agent

Analyzes affected areas and determines response priority using
population impact, urgency, vulnerability, resource shortages,
and accessibility constraints.
"""

from crewai import Agent, LLM

from config.settings import (
    AGENT_TEMPERATURE,
    get_groq_api_key,
    get_groq_model,
)


def create_priority_agent() -> Agent:
    """
    Create and return the Priority & Impact Agent.
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
        role="Emergency Priority and Impact Specialist",

        goal=(
            "Analyze affected areas and determine their response "
            "priority using evidence from situation intelligence, "
            "identified needs, resource constraints, and logistics "
            "conditions. Consider population impact, urgency, "
            "vulnerability, severity, shortages, and accessibility. "
            "Provide transparent reasoning for each priority decision "
            "and clearly identify uncertainty or missing information."
        ),

        backstory=(
            "You are the Priority and Impact Agent in RESONA. "
            "You specialize in evidence-based emergency prioritization. "
            "Your responsibility is to help determine which areas "
            "require faster or greater attention when resources are "
            "limited. You do not rely on population size alone. "
            "You consider multiple factors including emergency "
            "severity, urgent medical or humanitarian needs, affected "
            "population, vulnerable groups, resource shortages, and "
            "accessibility constraints. You make the factors behind "
            "your assessment explicit so that another agent can "
            "review and challenge the recommendation."
        ),

        llm=llm,

        verbose=False,

        allow_delegation=False,

        max_iter=5,
    )
