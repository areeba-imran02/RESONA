"""
RESONA - Multi-Agent Emergency Response Workflow

Implements the actual RESONA orchestration pipeline:

1. Situation Intelligence
2. Needs Assessment
3. Resource Intelligence
4. Logistics & Deployment
5. Priority & Impact
6. Critic & Conflict Resolution
7. Conditional agent re-evaluation
8. Final Critic review
9. Response Coordinator
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type

from crewai import Task
from pydantic import BaseModel

from config.settings import MAX_AGENT_REVISIONS
from crew.crew_manager import ResonaCrewManager
from crew.schemas import (
    SituationAssessment,
    NeedsAssessment,
    ResourceAssessment,
    LogisticsAssessment,
    PriorityAssessment,
    CriticAssessment,
    ResponsePlan,
    WorkflowState,
    AgentExecutionRecord,
)


class ResonaWorkflow:
    """Runs the complete RESONA multi-agent emergency workflow."""

    def __init__(self):
        self.manager = ResonaCrewManager()

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _model_to_dict(model: Optional[BaseModel]) -> Dict[str, Any]:
        if model is None:
            return {}

        if hasattr(model, "model_dump"):
            return model.model_dump()

        return model.dict()

    @staticmethod
    def _model_to_text(model: Optional[BaseModel]) -> str:
        if model is None:
            return "No structured output available."

        return json.dumps(
            ResonaWorkflow._model_to_dict(model),
            indent=2,
            ensure_ascii=False,
        )

    @staticmethod
    def _extract_model(task_output: Any, model_class: Type[BaseModel]):
        """
        Extract CrewAI's Pydantic result.

        CrewAI normally exposes structured output through
        task_output.pydantic.

        A JSON fallback is also provided for resilience.
        """

        if task_output is None:
            return None

        structured = getattr(task_output, "pydantic", None)

        if structured is not None:
            if isinstance(structured, model_class):
                return structured

            try:
                return model_class.model_validate(structured)
            except Exception:
                try:
                    return model_class.parse_obj(structured)
                except Exception:
                    pass

        raw = getattr(task_output, "raw", None)

        if raw:
            try:
                data = json.loads(raw)

                if hasattr(model_class, "model_validate"):
                    return model_class.model_validate(data)

                return model_class.parse_obj(data)

            except Exception:
                pass

        return None

    @staticmethod
    def _summary(model: Optional[BaseModel]) -> str:
        """Create a concise UI-safe summary without exposing chain-of-thought."""

        if model is None:
            return "No structured result returned."

        data = ResonaWorkflow._model_to_dict(model)

        if isinstance(model, SituationAssessment):
            return (
                f"{model.overall_severity.title()} emergency affecting "
                f"{model.affected_population:,} people across "
                f"{len(model.affected_areas)} area(s)."
            )

        if isinstance(model, NeedsAssessment):
            return (
                f"{len(model.needs)} needs identified; "
                f"{len(model.critical_needs)} marked critical."
            )

        if isinstance(model, ResourceAssessment):
            return (
                f"{len(model.available_resources)} resource types analyzed; "
                f"{len(model.resource_gaps)} resource gaps detected."
            )

        if isinstance(model, LogisticsAssessment):
            return (
                f"{len(model.deployment_options)} deployment options analyzed; "
                f"{len(model.operational_bottlenecks)} bottleneck(s) identified."
            )

        if isinstance(model, PriorityAssessment):
            return (
                f"{len(model.priority_areas)} priority area(s) identified; "
                f"{len(model.high_urgency_areas)} high-urgency area(s)."
            )

        if isinstance(model, CriticAssessment):
            return (
                f"{len(model.conflicts_detected)} conflict(s) detected; "
                f"re-evaluation={'required' if model.requires_re_evaluation else 'not required'}."
            )

        if isinstance(model, ResponsePlan):
            return (
                f"{len(model.priority_areas)} priority area(s), "
                f"{len(model.resource_allocations)} allocation(s), "
                f"{len(model.immediate_actions)} immediate action(s)."
            )

        return f"Structured result generated with {len(data)} fields."

    def _record(
        self,
        state: WorkflowState,
        agent_name: str,
        status: str,
        model: Optional[BaseModel] = None,
        revision: int = 0,
        upstream: Optional[list] = None,
        downstream: Optional[list] = None,
    ) -> None:
        state.agent_history.append(
            AgentExecutionRecord(
                agent_name=agent_name,
                status=status,
                input_summary="Structured workflow context",
                output_summary=self._summary(model),
                tools_used=[],
                upstream_agents=upstream or [],
                downstream_agents=downstream or [],
                revision=revision,
                timestamp=self._timestamp(),
            )
        )

    # ------------------------------------------------------------------
    # Initial workflow
    # ------------------------------------------------------------------

    def _create_initial_tasks(self, emergency_context: str):
        situation_task = Task(
            description=f"""
You are the Situation Intelligence Agent for RESONA.

Analyze the emergency information below.

Your job is to identify:
- emergency type
- location
- overall severity
- affected population
- affected areas
- critical conditions
- operational constraints
- missing information
- confidence level

Do not invent facts.

Return only a structured SituationAssessment.

EMERGENCY INFORMATION:
{emergency_context}
""",
            expected_output="A structured SituationAssessment.",
            agent=self.manager.situation_agent,
            output_pydantic=SituationAssessment,
        )

        needs_task = Task(
            description="""
Analyze the emergency situation produced by the Situation Intelligence Agent.

Determine:
- humanitarian needs
- critical needs
- vulnerable groups
- estimated quantities where evidence allows
- urgency
- information gaps
- confidence

Do not invent unsupported quantities.

Return a structured NeedsAssessment.
""",
            expected_output="A structured NeedsAssessment.",
            agent=self.manager.needs_agent,
            context=[situation_task],
            output_pydantic=NeedsAssessment,
        )

        resource_task = Task(
            description="""
Analyze the situation and needs assessment.

Determine:
- available resources
- resource shortages
- constrained resources
- surplus resources
- allocation constraints
- confidence

Perform quantitative reasoning where possible.

Return a structured ResourceAssessment.
""",
            expected_output="A structured ResourceAssessment.",
            agent=self.manager.resource_agent,
            context=[situation_task, needs_task],
            output_pydantic=ResourceAssessment,
        )

        logistics_task = Task(
            description="""
Analyze the situation, needs, and resource assessments.

Determine:
- feasible deployment options
- accessibility constraints
- transportation constraints
- operational bottlenecks
- recommended deployment sequence
- confidence

Do not assume inaccessible routes are usable.

Return a structured LogisticsAssessment.
""",
            expected_output="A structured LogisticsAssessment.",
            agent=self.manager.logistics_agent,
            context=[
                situation_task,
                needs_task,
                resource_task,
            ],
            output_pydantic=LogisticsAssessment,
        )

        priority_task = Task(
            description="""
Analyze all previous assessments.

Determine emergency response priorities using transparent factors such as:
- population impact
- severity
- urgency
- vulnerability
- resource shortage
- accessibility constraints

Do not simply prioritize the largest population.
Consider competing humanitarian needs and operational feasibility.

Return a structured PriorityAssessment.
""",
            expected_output="A structured PriorityAssessment.",
            agent=self.manager.priority_agent,
            context=[
                situation_task,
                needs_task,
                resource_task,
                logistics_task,
            ],
            output_pydantic=PriorityAssessment,
        )

        critic_task = Task(
            description="""
Act as the independent Critic & Conflict Resolution Agent.

Review every previous assessment.

Identify:
- conflicting recommendations
- unsupported assumptions
- missing information
- feasibility issues
- contradictions between urgency and population impact
- contradictions between needs and available resources
- logistics conflicts
- allocation risks

If an earlier agent should reconsider its result, set:
requires_re_evaluation = true

and specify the relevant agent names in:
agents_to_re_evaluate

Do not invent conflicts merely to force a revision.

Return a structured CriticAssessment.
""",
            expected_output="A structured CriticAssessment.",
            agent=self.manager.critic_agent,
            context=[
                situation_task,
                needs_task,
                resource_task,
                logistics_task,
                priority_task,
            ],
            output_pydantic=CriticAssessment,
        )

        return [
            situation_task,
            needs_task,
            resource_task,
            logistics_task,
            priority_task,
            critic_task,
        ]

    def _run_initial_analysis(
        self,
        emergency_context: str,
        state: WorkflowState,
    ) -> Dict[str, Any]:

        tasks = self._create_initial_tasks(emergency_context)

        crew = self.manager.create_crew(
            agents=[
                self.manager.situation_agent,
                self.manager.needs_agent,
                self.manager.resource_agent,
                self.manager.logistics_agent,
                self.manager.priority_agent,
                self.manager.critic_agent,
            ],
            tasks=tasks,
        )

        result = crew.kickoff()

        outputs = result.tasks_output

        state.situation = self._extract_model(
            outputs[0],
            SituationAssessment,
        )

        state.needs = self._extract_model(
            outputs[1],
            NeedsAssessment,
        )

        state.resources = self._extract_model(
            outputs[2],
            ResourceAssessment,
        )

        state.logistics = self._extract_model(
            outputs[3],
            LogisticsAssessment,
        )

        state.priority = self._extract_model(
            outputs[4],
            PriorityAssessment,
        )

        state.critic = self._extract_model(
            outputs[5],
            CriticAssessment,
        )

        self._record(
            state,
            "Situation Intelligence Agent",
            "completed",
            state.situation,
            upstream=[],
            downstream=["Needs Assessment Agent"],
        )

        self._record(
            state,
            "Needs Assessment Agent",
            "completed",
            state.needs,
            upstream=["Situation Intelligence Agent"],
            downstream=["Resource Intelligence Agent"],
        )

        self._record(
            state,
            "Resource Intelligence Agent",
            "completed",
            state.resources,
            upstream=["Situation Intelligence Agent", "Needs Assessment Agent"],
            downstream=["Logistics & Deployment Agent"],
        )

        self._record(
            state,
            "Logistics & Deployment Agent",
            "completed",
            state.logistics,
            upstream=["Situation Intelligence Agent", "Needs Assessment Agent"],
            downstream=["Priority & Impact Agent"],
        )

        self._record(
            state,
            "Priority & Impact Agent",
            "completed",
            state.priority,
            upstream=[
                "Needs Assessment Agent",
                "Resource Intelligence Agent",
                "Logistics & Deployment Agent",
            ],
            downstream=["Critic & Conflict Resolution Agent"],
        )

        self._record(
            state,
            "Critic & Conflict Resolution Agent",
            "completed",
            state.critic,
            upstream=[
                "Situation Intelligence Agent",
                "Needs Assessment Agent",
                "Resource Intelligence Agent",
                "Logistics & Deployment Agent",
                "Priority & Impact Agent",
            ],
            downstream=["Response Coordinator Agent"],
        )

        return {
            "crew_result": result,
            "tasks": tasks,
        }

    # ------------------------------------------------------------------
    # Targeted re-evaluation
    # ------------------------------------------------------------------

    def _build_revision_task(
        self,
        agent_name: str,
        emergency_context: str,
        state: WorkflowState,
    ) -> Optional[Task]:

        agent = self.manager.get_agent(agent_name)

        if agent is None:
            return None

        evidence = {
            "situation": self._model_to_dict(state.situation),
            "needs": self._model_to_dict(state.needs),
            "resources": self._model_to_dict(state.resources),
            "logistics": self._model_to_dict(state.logistics),
            "priority": self._model_to_dict(state.priority),
            "critic": self._model_to_dict(state.critic),
        }

        descriptions = {
            "Situation Intelligence Agent": """
Re-evaluate the SituationAssessment using the critic's findings.
Correct only evidence-supported issues.
""",
            "Needs Assessment Agent": """
Re-evaluate the NeedsAssessment using the critic's findings.
Pay special attention to urgency, quantities, vulnerability,
and unsupported assumptions.
""",
            "Resource Intelligence Agent": """
Re-evaluate the ResourceAssessment using the critic's findings.
Check shortages, constraints, and whether allocations are feasible.
""",
            "Logistics & Deployment Agent": """
Re-evaluate the LogisticsAssessment using the critic's findings.
Check accessibility, transportation, and deployment feasibility.
""",
            "Priority & Impact Agent": """
Re-evaluate the PriorityAssessment using the critic's findings.
Resolve conflicts between population impact, urgency, vulnerability,
shortages, and accessibility.
""",
        }

        description = descriptions.get(agent_name)

        if not description:
            return None

        model_map = {
            "Situation Intelligence Agent": SituationAssessment,
            "Needs Assessment Agent": NeedsAssessment,
            "Resource Intelligence Agent": ResourceAssessment,
            "Logistics & Deployment Agent": LogisticsAssessment,
            "Priority & Impact Agent": PriorityAssessment,
        }

        model_class = model_map[agent_name]

        return Task(
            description=f"""
{description}

This is a targeted revision, not a completely new analysis.

Original emergency context:
{emergency_context}

Current assessments:
{json.dumps(evidence, indent=2, ensure_ascii=False)}

Return the corrected structured {model_class.__name__}.

Do not blindly accept the critic.
Only change conclusions when supported by the available evidence.
""",
            expected_output=f"A revised structured {model_class.__name__}.",
            agent=agent,
            output_pydantic=model_class,
        )

    def _apply_revision(
        self,
        agent_name: str,
        revised_model: BaseModel,
        state: WorkflowState,
    ) -> None:

        mapping = {
            "Situation Intelligence Agent": "situation",
            "Needs Assessment Agent": "needs",
            "Resource Intelligence Agent": "resources",
            "Logistics & Deployment Agent": "logistics",
            "Priority & Impact Agent": "priority",
        }

        attribute = mapping.get(agent_name)

        if attribute:
            setattr(state, attribute, revised_model)

    def _run_re_evaluation(
        self,
        emergency_context: str,
        state: WorkflowState,
    ) -> None:

        if not state.critic:
            return

        if not state.critic.requires_re_evaluation:
            return

        if state.revision_count >= MAX_AGENT_REVISIONS:
            return

        agents_to_revise = [
            name
            for name in state.critic.agents_to_re_evaluate
            if name != "Critic & Conflict Resolution Agent"
        ]

        if not agents_to_revise:
            return

        state.revision_count += 1

        for agent_name in agents_to_revise:
            task = self._build_revision_task(
                agent_name=agent_name,
                emergency_context=emergency_context,
                state=state,
            )

            if task is None:
                continue

            agent = self.manager.get_agent(agent_name)

            crew = self.manager.create_single_agent_crew(
                agent=agent,
                task=task,
            )

            result = crew.kickoff()

            if not result.tasks_output:
                continue

            revised_model = self._extract_model(
                result.tasks_output[0],
                type(
                    "DynamicModel",
                    (BaseModel,),
                    {},
                ),
            )

            # CrewAI normally exposes the actual Pydantic object.
            structured = getattr(
                result.tasks_output[0],
                "pydantic",
                None,
            )

            if structured is not None:
                revised_model = structured

            if revised_model is not None:
                self._apply_revision(
                    agent_name,
                    revised_model,
                    state,
                )

                self._record(
                    state,
                    agent_name,
                    "revised",
                    revised_model,
                    revision=state.revision_count,
                    upstream=["Critic & Conflict Resolution Agent"],
                    downstream=["Critic & Conflict Resolution Agent"],
                )

        # Critic reviews revised findings again.
        self._run_final_critic_review(state)

    # ------------------------------------------------------------------
    # Final critic
    # ------------------------------------------------------------------

    def _run_final_critic_review(self, state: WorkflowState) -> None:

        review_context = json.dumps(
            {
                "situation": self._model_to_dict(state.situation),
                "needs": self._model_to_dict(state.needs),
                "resources": self._model_to_dict(state.resources),
                "logistics": self._model_to_dict(state.logistics),
                "priority": self._model_to_dict(state.priority),
                "previous_critic": self._model_to_dict(state.critic),
            },
            indent=2,
            ensure_ascii=False,
        )

        task = Task(
            description=f"""
Perform a final independent review of the revised RESONA analysis.

Check:
- remaining contradictions
- feasibility
- resource limitations
- priority consistency
- logistics consistency
- unsupported assumptions
- unresolved information gaps

Do not create unnecessary conflicts.

Return a structured CriticAssessment.

CURRENT ANALYSIS:
{review_context}
""",
            expected_output="A final structured CriticAssessment.",
            agent=self.manager.critic_agent,
            output_pydantic=CriticAssessment,
        )

        crew = self.manager.create_single_agent_crew(
            agent=self.manager.critic_agent,
            task=task,
        )

        result = crew.kickoff()

        if result.tasks_output:
            critic = self._extract_model(
                result.tasks_output[0],
                CriticAssessment,
            )

            if critic:
                state.critic = critic

                self._record(
                    state,
                    "Critic & Conflict Resolution Agent",
                    "reviewed",
                    critic,
                    revision=state.revision_count,
                    upstream=[
                        "Re-evaluated Agents"
                    ],
                    downstream=["Response Coordinator Agent"],
                )

    # ------------------------------------------------------------------
    # Coordinator
    # ------------------------------------------------------------------

    def _run_coordinator(
        self,
        state: WorkflowState,
    ) -> ResponsePlan:

        final_context = json.dumps(
            {
                "situation": self._model_to_dict(state.situation),
                "needs": self._model_to_dict(state.needs),
                "resources": self._model_to_dict(state.resources),
                "logistics": self._model_to_dict(state.logistics),
                "priority": self._model_to_dict(state.priority),
                "critic": self._model_to_dict(state.critic),
            },
            indent=2,
            ensure_ascii=False,
        )

        task = Task(
            description=f"""
You are the Response Coordinator Agent for RESONA.

Synthesize the reviewed multi-agent findings into one practical,
coordinated emergency response plan.

The final plan must include:
- emergency summary
- situation assessment
- priority areas
- resource allocations
- logistics and deployment
- volunteer assignments where appropriate
- conflicts and how they were resolved
- information gaps
- immediate actions
- confidence
- uncertainty notes

Respect actual resource constraints.

Do not invent resources.

Do not expose internal chain-of-thought.
Return only the structured ResponsePlan.

REVIEWED MULTI-AGENT ANALYSIS:
{final_context}
""",
            expected_output="A structured ResponsePlan.",
            agent=self.manager.coordinator_agent,
            output_pydantic=ResponsePlan,
        )

        crew = self.manager.create_single_agent_crew(
            agent=self.manager.coordinator_agent,
            task=task,
        )

        result = crew.kickoff()

        if not result.tasks_output:
            raise RuntimeError(
                "Response Coordinator did not return a result."
            )

        response_plan = self._extract_model(
            result.tasks_output[0],
            ResponsePlan,
        )

        if response_plan is None:
            raise RuntimeError(
                "Response Coordinator returned an invalid structured response."
            )

        self._record(
            state,
            "Response Coordinator Agent",
            "completed",
            response_plan,
            revision=state.revision_count,
            upstream=["Critic & Conflict Resolution Agent"],
            downstream=[],
        )

        return response_plan

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        emergency_context: str,
        emergency_id: str,
    ) -> Dict[str, Any]:

        if not emergency_context.strip():
            raise ValueError("Emergency context cannot be empty.")

        state = WorkflowState(
            emergency_id=emergency_id,
            workflow_status="running",
        )

        try:
            # Phase 1: independent multi-agent analysis
            self._run_initial_analysis(
                emergency_context=emergency_context,
                state=state,
            )

            # Phase 2: conditional re-evaluation
            if (
                state.critic
                and state.critic.requires_re_evaluation
            ):
                self._run_re_evaluation(
                    emergency_context=emergency_context,
                    state=state,
                )

            # Phase 3: final coordinated response
            state.final_response = self._run_coordinator(
                state=state,
            )

            state.workflow_status = "completed"

            return {
                "success": True,
                "state": state,
                "final_response": state.final_response,
                "error": None,
            }

        except Exception as exc:

            state.workflow_status = "failed"

            return {
                "success": False,
                "state": state,
                "final_response": None,
                "error": str(exc),
            }
