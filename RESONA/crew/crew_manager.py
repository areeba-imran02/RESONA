"""
RESONA - Crew Manager

Creates and manages the specialized CrewAI agents used by RESONA.
"""

from crewai import Crew, Process

from agents.situation_agent import create_situation_agent
from agents.needs_agent import create_needs_agent
from agents.resource_agent import create_resource_agent
from agents.logistics_agent import create_logistics_agent
from agents.priority_agent import create_priority_agent
from agents.critic_agent import create_critic_agent
from agents.coordinator_agent import create_coordinator_agent


class ResonaCrewManager:
    """Central manager for the RESONA CrewAI agent team."""

    def __init__(self):
        self.situation_agent = create_situation_agent()
        self.needs_agent = create_needs_agent()
        self.resource_agent = create_resource_agent()
        self.logistics_agent = create_logistics_agent()
        self.priority_agent = create_priority_agent()
        self.critic_agent = create_critic_agent()
        self.coordinator_agent = create_coordinator_agent()

    def get_agents(self) -> list:
        return [
            self.situation_agent,
            self.needs_agent,
            self.resource_agent,
            self.logistics_agent,
            self.priority_agent,
            self.critic_agent,
            self.coordinator_agent,
        ]

    def get_agent(self, agent_name: str):
        """Return an agent by its RESONA workflow name."""

        mapping = {
            "Situation Intelligence Agent": self.situation_agent,
            "Needs Assessment Agent": self.needs_agent,
            "Resource Intelligence Agent": self.resource_agent,
            "Logistics & Deployment Agent": self.logistics_agent,
            "Priority & Impact Agent": self.priority_agent,
            "Critic & Conflict Resolution Agent": self.critic_agent,
            "Response Coordinator Agent": self.coordinator_agent,
        }

        return mapping.get(agent_name)

    def create_crew(self, agents: list, tasks: list) -> Crew:
        """Create a CrewAI sequential crew."""

        if not agents:
            raise ValueError("At least one agent is required.")

        if not tasks:
            raise ValueError("At least one task is required.")

        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=False,
        )

    def create_single_agent_crew(self, agent, task) -> Crew:
        """Create a one-agent crew for targeted re-evaluation."""

        return self.create_crew(
            agents=[agent],
            tasks=[task],
        )
