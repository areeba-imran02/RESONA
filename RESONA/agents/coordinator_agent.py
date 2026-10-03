"""
RESONA - Response Coordinator Agent

Synthesizes reviewed emergency intelligence into a coordinated
and actionable response plan.
"""

from crewai import Agent, LLM

from config.settings import (
    AGENT_TEMPERATURE,
    get_groq_api_key,
    get_groq_model,
)


def create_coordinator_agent() -> Agent:
    """
    Create and return the Response Coordinator Agent.
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
        role="Emergency Response Coordinator",

        goal=(
            "Synthesize the reviewed outputs from all specialized "
            "RESONA agents into one coherent, practical, and "
            "evidence-based emergency response plan. Incorporate "
            "situation intelligence, assessed needs, available "
            "resources, logistics constraints, priority analysis, "
            "and critic findings. Resolve competing recommendations "
            "using the available evidence and clearly communicate "
            "uncertainty, information gaps, resource limitations, "
            "and immediate response actions."
        ),

        backstory=(
            "You are the Response Coordinator at the center of "
            "RESONA's emergency intelligence workflow. Specialized "
            "agents provide you with situation analysis, needs "
            "assessment, resource intelligence, logistics planning, "
            "and priority analysis. A separate critic layer reviews "
            "those findings for conflicts and feasibility problems "
            "before you make the final coordination plan. Your role "
            "is to integrate the reviewed information rather than "
            "blindly accepting any single agent's recommendation. "
            "You must respect actual resource limitations and "
            "accessibility constraints. You must never invent "
            "resources, people, locations, or facts that were not "
            "provided or reasonably derived from the available "
            "information."
        ),

        llm=llm,

        verbose=False,

        allow_delegation=False,

        max_iter=5,
    )
