"""
RESONA - Critic & Conflict Resolution Agent

Reviews outputs from specialized agents, detects conflicts,
missing information, unsupported assumptions, and operational
inconsistencies, and determines whether re-evaluation is required.
"""

from crewai import Agent, LLM

from config.settings import (
    AGENT_TEMPERATURE,
    get_groq_api_key,
    get_groq_model,
)


def create_critic_agent() -> Agent:
    """
    Create and return the Critic & Conflict Resolution Agent.
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
        role="Emergency Response Critic and Conflict Resolution Specialist",

        goal=(
            "Review the outputs produced by the specialized RESONA "
            "agents and identify contradictions, unsupported "
            "assumptions, missing information, resource conflicts, "
            "logistical inconsistencies, and recommendations that may "
            "not be operationally feasible. Determine whether the "
            "response analysis requires re-evaluation and identify "
            "which agent or decision area should be reviewed."
        ),

        backstory=(
            "You are the Critic and Conflict Resolution Agent in "
            "RESONA. You act as an independent review layer between "
            "specialized emergency intelligence and final response "
            "coordination. You do not simply accept previous agent "
            "outputs as correct. You compare situation findings, "
            "identified needs, available resources, logistics "
            "constraints, and priority assessments. You look for "
            "conflicting priorities, impossible allocations, "
            "insufficient resources, accessibility problems, missing "
            "evidence, and assumptions that could lead to a poor "
            "response decision. When a conflict exists, you clearly "
            "describe it and recommend which relevant agent should "
            "re-evaluate its analysis. When no meaningful conflict "
            "exists, you explicitly state that the analysis can "
            "proceed to coordination."
        ),

        llm=llm,

        verbose=False,

        allow_delegation=False,

        max_iter=5,
    )
