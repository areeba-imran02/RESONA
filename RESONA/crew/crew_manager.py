"""
RESONA - Crew Manager

Creates and manages the seven specialized RESONA agents
using CrewAI.
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
    """
    Central manager responsible for creating the RESONA
    multi-agent team.
    """

    def __init__(self):
        self.situation_agent = create_situation_agent()
        self.needs_agent = create_needs_agent()
        self.resource_agent = create_resource_agent()
        self.logistics_agent = create_logistics_agent()
        self.priority_agent = create_priority_agent()
        self.critic_agent = create_critic_agent()
        self.coordinator_agent = create_coordinator_agent()

    def get_agents(self) -> list:
        """
        Return all RESONA agents in workflow order.
        """

        return [
            self.situation_agent,
            self.needs_agent,
            self.resource_agent,
            self.logistics_agent,
            self.priority_agent,
            self.critic_agent,
            self.coordinator_agent,
        ]

    def create_crew(self, tasks: list) -> Crew:
        """
        Create a CrewAI crew using the supplied tasks.

        Tasks are supplied by the workflow layer so that
        dynamic emergency data can be passed into the team.
        """

        if not tasks:
            raise ValueError(
                "At least one task is required to create the RESONA crew."
            )

        return Crew(
            agents=self.get_agents(),
            tasks=tasks,
            process=Process.sequential,
            verbose=False,
        )
