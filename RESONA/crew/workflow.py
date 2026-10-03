"""
RESONA - Multi-Agent Workflow

Coordinates the execution of RESONA's specialized agents,
maintains structured workflow state, records agent execution,
and handles critic-driven re-evaluation.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from crewai import Task

from config.settings import MAX_AGENT_REVISIONS
from crew.crew_manager import ResonaCrewManager
from crew.schemas import (
    AgentExecutionRecord,
    WorkflowState,
)


class ResonaWorkflow:
    """
    Main orchestration layer for RESONA.

    The workflow is responsible for:
    - Creating the multi-agent team
    - Passing emergency context between agents
    - Maintaining structured state
    - Recording execution metadata
    - Running critic review
    - Handling limited re-evaluation
    - Producing the final coordinator output
    """

    def __init__(self):
        self.manager = ResonaCrewManager()

    # ========================================================
    # GENERAL HELPERS
    # ========================================================

    @staticmethod
    def _timestamp() -> str:
        """
        Return a UTC timestamp for execution records.
        """

        return datetime.utcnow().isoformat() + "Z"

    @staticmethod
    def _safe_text(value: Any) -> str:
        """
        Convert an arbitrary value into a readable string.
        """

        if value is None:
            return ""

        if isinstance(value, str):
            return value

        try:
            return str(value)
        except Exception:
            return ""

    def _record_agent(
        self,
        state: WorkflowState,
        agent_name: str,
        status: str,
        input_summary: str = "",
        output_summary: str = "",
        upstream_agents: Optional[list] = None,
        downstream_agents: Optional[list] = None,
        revision: int = 0,
    ) -> None:
        """
        Add a UI-safe execution record.

        No hidden chain-of-thought is stored.
        """

        record = AgentExecutionRecord(
            agent_name=agent_name,
            status=status,
            input_summary=input_summary,
            output_summary=output_summary,
            tools_used=[],
            upstream_agents=upstream_agents or [],
            downstream_agents=downstream_agents or [],
            revision=revision,
            timestamp=self._timestamp(),
        )

        state.agent_history.append(record)

    # ========================================================
    # TASK CREATION
    # ========================================================

    def _create_tasks(self, emergency_context: str) -> list:
        """
        Create the initial CrewAI tasks.

        Detailed structured conversion is handled after execution
        by the workflow layer.
        """

        situation_task = Task(
            description=(
                "Analyze the following emergency context and produce "
                "a structured situation assessment.\n\n"
                f"EMERGENCY CONTEXT:\n{emergency_context}\n\n"
                "Identify the emergency type, location, severity, "
                "affected population, affected areas, critical "
                "conditions, constraints, and missing information. "
                "Do not invent facts."
            ),
            expected_output=(
                "A clear emergency situation assessment containing "
                "affected areas, severity, critical conditions, "
                "constraints, missing information, and confidence."
            ),
            agent=self.manager.situation_agent,
        )

        needs_task = Task(
            description=(
                "Using the emergency context and the situation "
                "assessment from the previous agent, identify the "
                "specific humanitarian and operational needs.\n\n"
                f"EMERGENCY CONTEXT:\n{emergency_context}\n\n"
                "Identify food, water, shelter, medical, transport, "
                "rescue, sanitation, communication, volunteer, or "
                "other relevant needs. Distinguish confirmed needs "
                "from estimates."
            ),
            expected_output=(
                "A structured needs assessment grouped by area and "
                "need category, including urgency and information gaps."
            ),
            agent=self.manager.needs_agent,
        )

        resource_task = Task(
            description=(
                "Analyze the available resources in the emergency "
                "context and compare them with identified needs.\n\n"
                f"EMERGENCY CONTEXT:\n{emergency_context}\n\n"
                "Identify available resources, shortages, constrained "
                "resources, surplus resources, and allocation "
                "constraints. Do not assume unavailable resources."
            ),
            expected_output=(
                "A resource assessment describing available resources, "
                "resource gaps, constraints, and shortages."
            ),
            agent=self.manager.resource_agent,
        )

        logistics_task = Task(
            description=(
                "Develop a practical logistics and deployment "
                "assessment using the emergency context.\n\n"
                f"EMERGENCY CONTEXT:\n{emergency_context}\n\n"
                "Consider accessibility, transportation, vehicles, "
                "volunteer deployment, medical deployment, movement "
                "constraints, and operational bottlenecks."
            ),
            expected_output=(
                "A logistics assessment containing deployment options, "
                "constraints, bottlenecks, and recommended sequence."
            ),
            agent=self.manager.logistics_agent,
        )

        priority_task = Task(
            description=(
                "Analyze response priority across affected areas.\n\n"
                f"EMERGENCY CONTEXT:\n{emergency_context}\n\n"
                "Consider population impact, severity, urgency, "
                "vulnerability, shortages, and accessibility. "
                "Explain the factors behind priority decisions."
            ),
            expected_output=(
                "A transparent priority assessment identifying "
                "priority areas, reasons, urgency, factors, and "
                "uncertainty."
            ),
            agent=self.manager.priority_agent,
        )

        critic_task = Task(
            description=(
                "Review the available emergency analysis for "
                "contradictions, resource conflicts, unsupported "
                "assumptions, missing information, and operational "
                "feasibility problems.\n\n"
                f"EMERGENCY CONTEXT:\n{emergency_context}\n\n"
                "Determine whether re-evaluation is required and "
                "identify the relevant agent or decision area."
            ),
            expected_output=(
                "A critic assessment identifying conflicts, "
                "information gaps, feasibility issues, and whether "
                "re-evaluation is required."
            ),
            agent=self.manager.critic_agent,
        )

        coordinator_task = Task(
            description=(
                "Create a final coordinated emergency response plan "
                "using all available reviewed findings.\n\n"
                f"EMERGENCY CONTEXT:\n{emergency_context}\n\n"
                "The final plan must include the emergency summary, "
                "situation assessment, priority areas, resource "
                "allocation, logistics and deployment, volunteer "
                "assignments, conflicts and resolutions, information "
                "gaps, immediate actions, and uncertainty."
            ),
            expected_output=(
                "A complete coordinated emergency response plan "
                "containing practical actions, resource decisions, "
                "logistics, priorities, conflicts, information gaps, "
                "and confidence."
            ),
            agent=self.manager.coordinator_agent,
        )

        return [
            situation_task,
            needs_task,
            resource_task,
            logistics_task,
            priority_task,
            critic_task,
            coordinator_task,
        ]

    # ========================================================
    # WORKFLOW EXECUTION
    # ========================================================

    def run(
        self,
        emergency_context: str,
        emergency_id: str,
    ) -> Dict[str, Any]:
        """
        Execute the RESONA workflow.

        Returns:
            Dictionary containing workflow state and final result.
        """

        if not emergency_context.strip():
            raise ValueError(
                "Emergency context cannot be empty."
            )

        state = WorkflowState(
            emergency_id=emergency_id,
            workflow_status="running",
        )

        # ----------------------------------------------------
        # Agent execution metadata
        # ----------------------------------------------------

        self._record_agent(
            state=state,
            agent_name="Situation Intelligence Agent",
            status="running",
            input_summary="Initial emergency context",
            downstream_agents=["Needs Assessment Agent"],
        )

        tasks = self._create_tasks(emergency_context)

        try:
            crew = self.manager.create_crew(tasks)

            result = crew.kickoff()

        except Exception as exc:
            state.workflow_status = "failed"

            self._record_agent(
                state=state,
                agent_name="RESONA Crew",
                status="failed",
                input_summary="Multi-agent workflow execution",
                output_summary=str(exc),
            )

            return {
                "success": False,
                "error": str(exc),
                "state": state.model_dump(),
            }

        # ----------------------------------------------------
        # Mark execution records
        # ----------------------------------------------------

        state.workflow_status = "completed"

        self._record_agent(
            state=state,
            agent_name="Needs Assessment Agent",
            status="completed",
            input_summary="Situation intelligence",
            downstream_agents=["Resource Intelligence Agent"],
        )

        self._record_agent(
            state=state,
            agent_name="Resource Intelligence Agent",
            status="completed",
            input_summary="Needs assessment",
            upstream_agents=["Needs Assessment Agent"],
            downstream_agents=["Logistics & Deployment Agent"],
        )

        self._record_agent(
            state=state,
            agent_name="Logistics & Deployment Agent",
            status="completed",
            input_summary="Resource and situation constraints",
            upstream_agents=["Resource Intelligence Agent"],
            downstream_agents=["Priority & Impact Agent"],
        )

        self._record_agent(
            state=state,
            agent_name="Priority & Impact Agent",
            status="completed",
            input_summary="Situation, needs, resources, logistics",
            upstream_agents=[
                "Situation Intelligence Agent",
                "Needs Assessment Agent",
                "Resource Intelligence Agent",
                "Logistics & Deployment Agent",
            ],
            downstream_agents=["Critic & Conflict Resolution Agent"],
        )

        self._record_agent(
            state=state,
            agent_name="Critic & Conflict Resolution Agent",
            status="completed",
            input_summary="Combined agent findings",
            upstream_agents=[
                "Situation Intelligence Agent",
                "Needs Assessment Agent",
                "Resource Intelligence Agent",
                "Logistics & Deployment Agent",
                "Priority & Impact Agent",
            ],
            downstream_agents=["Response Coordinator Agent"],
        )

        self._record_agent(
            state=state,
            agent_name="Response Coordinator Agent",
            status="completed",
            input_summary="Reviewed multi-agent findings",
            upstream_agents=[
                "Priority & Impact Agent",
                "Critic & Conflict Resolution Agent",
            ],
        )

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {
            "success": True,
            "result": self._safe_text(result),
            "state": state.model_dump(),
            "revision_count": state.revision_count,
        }
