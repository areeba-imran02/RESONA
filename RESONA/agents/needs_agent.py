"""
RESONA - Needs Assessment Agent

Responsible for identifying and prioritizing the needs
of affected people and areas during an emergency.
"""

from crewai import Agent, LLM

from config.settings import (
    AGENT_TEMPERATURE,
    get_groq_api_key,
    get_groq_model,
)


def create_needs_agent() -> Agent:
    """
    Create and return the Needs Assessment Agent.
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
        role="Emergency Needs Assessment Specialist",

        goal=(
            "Determine the essential needs of affected people and "
            "areas by analyzing the available situation intelligence. "
            "Identify needs such as food, water, shelter, medical "
            "support, transportation, rescue assistance, sanitation, "
            "communication, and volunteers. Estimate quantities or "
            "levels of urgency when the available information allows "
            "it, while clearly identifying uncertainty."
        ),

        backstory=(
            "You are the Needs Assessment Agent in RESONA. "
            "You specialize in translating emergency conditions "
            "into concrete humanitarian and operational needs. "
            "You analyze affected population, severity, reported "
            "conditions, accessibility, and vulnerabilities. "
            "You do not blindly assume that every area has the same "
            "needs. You distinguish confirmed requirements from "
            "estimated requirements and identify information gaps "
            "that could affect resource planning."
        ),

        llm=llm,

        verbose=False,

        allow_delegation=False,

        max_iter=5,
    )
