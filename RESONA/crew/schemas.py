"""
RESONA - Crew Data Schemas

Shared Pydantic models used to pass structured information
between RESONA agents and the workflow.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# BASIC STRUCTURES
# ============================================================

class AffectedArea(BaseModel):
    """
    Structured information about an affected area.
    """

    name: str = Field(
        ...,
        description="Name or identifier of the affected area.",
    )

    affected_population: int = Field(
        default=0,
        ge=0,
        description="Estimated number of affected people.",
    )

    severity: str = Field(
        default="unknown",
        description="Overall emergency severity.",
    )

    accessibility: str = Field(
        default="unknown",
        description="Accessibility condition of the area.",
    )

    critical_conditions: List[str] = Field(
        default_factory=list,
        description="Important emergency conditions.",
    )

    notes: List[str] = Field(
        default_factory=list,
        description="Additional relevant observations.",
    )


class NeedItem(BaseModel):
    """
    Represents an identified emergency need.
    """

    area: str

    category: str

    description: str

    urgency: str = "medium"

    estimated_quantity: Optional[float] = None

    unit: Optional[str] = None

    confidence: str = "medium"


class ResourceItem(BaseModel):
    """
    Represents an available emergency resource.
    """

    name: str

    category: str

    quantity: float = Field(
        default=0,
        ge=0,
    )

    unit: Optional[str] = None

    location: Optional[str] = None

    available: bool = True

    notes: List[str] = Field(
        default_factory=list,
    )


class ResourceGap(BaseModel):
    """
    Represents a shortage or resource gap.
    """

    resource: str

    required_quantity: Optional[float] = None

    available_quantity: Optional[float] = None

    shortage_quantity: Optional[float] = None

    affected_area: Optional[str] = None

    severity: str = "medium"

    explanation: str = ""


class DeploymentOption(BaseModel):
    """
    Represents a logistics/deployment option.
    """

    area: str

    resource: str

    recommended_quantity: Optional[float] = None

    transport_method: Optional[str] = None

    accessibility_constraint: Optional[str] = None

    priority_sequence: Optional[int] = None

    feasibility: str = "unknown"

    notes: List[str] = Field(
        default_factory=list,
    )


# ============================================================
# AGENT OUTPUTS
# ============================================================

class SituationAssessment(BaseModel):
    """
    Structured output from the Situation Intelligence Agent.
    """

    emergency_type: str

    location: str

    overall_severity: str

    affected_population: int = Field(
        default=0,
        ge=0,
    )

    affected_areas: List[AffectedArea] = Field(
        default_factory=list,
    )

    critical_conditions: List[str] = Field(
        default_factory=list,
    )

    constraints: List[str] = Field(
        default_factory=list,
    )

    missing_information: List[str] = Field(
        default_factory=list,
    )

    confidence: str = "medium"


class NeedsAssessment(BaseModel):
    """
    Structured output from the Needs Assessment Agent.
    """

    needs: List[NeedItem] = Field(
        default_factory=list,
    )

    critical_needs: List[str] = Field(
        default_factory=list,
    )

    vulnerable_groups: List[str] = Field(
        default_factory=list,
    )

    information_gaps: List[str] = Field(
        default_factory=list,
    )

    confidence: str = "medium"


class ResourceAssessment(BaseModel):
    """
    Structured output from the Resource Intelligence Agent.
    """

    available_resources: List[ResourceItem] = Field(
        default_factory=list,
    )

    resource_gaps: List[ResourceGap] = Field(
        default_factory=list,
    )

    constrained_resources: List[str] = Field(
        default_factory=list,
    )

    surplus_resources: List[str] = Field(
        default_factory=list,
    )

    allocation_constraints: List[str] = Field(
        default_factory=list,
    )

    confidence: str = "medium"


class LogisticsAssessment(BaseModel):
    """
    Structured output from the Logistics & Deployment Agent.
    """

    deployment_options: List[DeploymentOption] = Field(
        default_factory=list,
    )

    accessibility_constraints: List[str] = Field(
        default_factory=list,
    )

    transportation_constraints: List[str] = Field(
        default_factory=list,
    )

    operational_bottlenecks: List[str] = Field(
        default_factory=list,
    )

    recommended_sequence: List[str] = Field(
        default_factory=list,
    )

    confidence: str = "medium"


class PriorityAssessment(BaseModel):
    """
    Structured output from the Priority & Impact Agent.
    """

    priority_areas: List[str] = Field(
        default_factory=list,
    )

    priority_reasons: Dict[str, List[str]] = Field(
        default_factory=dict,
    )

    high_urgency_areas: List[str] = Field(
        default_factory=list,
    )

    vulnerability_factors: Dict[str, List[str]] = Field(
        default_factory=dict,
    )

    scoring_factors: Dict[str, Any] = Field(
        default_factory=dict,
    )

    uncertainty: List[str] = Field(
        default_factory=list,
    )

    confidence: str = "medium"


class ConflictItem(BaseModel):
    """
    Represents a detected conflict between agent findings.
    """

    conflict_id: str

    description: str

    agents_involved: List[str] = Field(
        default_factory=list,
    )

    evidence: List[str] = Field(
        default_factory=list,
    )

    severity: str = "medium"

    requires_revision: bool = False

    recommended_reviewer: Optional[str] = None


class CriticAssessment(BaseModel):
    """
    Structured output from the Critic & Conflict Resolution Agent.
    """

    conflicts_detected: List[ConflictItem] = Field(
        default_factory=list,
    )

    missing_information: List[str] = Field(
        default_factory=list,
    )

    unsupported_assumptions: List[str] = Field(
        default_factory=list,
    )

    feasibility_issues: List[str] = Field(
        default_factory=list,
    )

    requires_re_evaluation: bool = False

    agents_to_re_evaluate: List[str] = Field(
        default_factory=list,
    )

    review_summary: str = ""


# ============================================================
# FINAL RESPONSE
# ============================================================

class ResourceAllocation(BaseModel):
    """
    Final resource allocation decision.
    """

    area: str

    resource: str

    quantity: Optional[float] = None

    unit: Optional[str] = None

    rationale: str = ""


class VolunteerAssignment(BaseModel):
    """
    Final volunteer deployment assignment.
    """

    volunteer_id: Optional[str] = None

    area: str

    task: str

    required_skills: List[str] = Field(
        default_factory=list,
    )

    notes: str = ""


class ResponsePlan(BaseModel):
    """
    Final coordinated emergency response plan.
    """

    emergency_summary: str

    situation_assessment: str

    priority_areas: List[str] = Field(
        default_factory=list,
    )

    resource_allocations: List[ResourceAllocation] = Field(
        default_factory=list,
    )

    logistics_and_deployment: List[DeploymentOption] = Field(
        default_factory=list,
    )

    volunteer_assignments: List[VolunteerAssignment] = Field(
        default_factory=list,
    )

    conflicts_and_resolutions: List[str] = Field(
        default_factory=list,
    )

    information_gaps: List[str] = Field(
        default_factory=list,
    )

    immediate_actions: List[str] = Field(
        default_factory=list,
    )

    confidence: str = "medium"

    uncertainty_notes: List[str] = Field(
        default_factory=list,
    )


# ============================================================
# WORKFLOW STATE
# ============================================================

class AgentExecutionRecord(BaseModel):
    """
    UI-safe record of one agent execution.

    This stores concise structured information only.
    It does NOT store hidden chain-of-thought.
    """

    agent_name: str

    status: str = "pending"

    input_summary: str = ""

    output_summary: str = ""

    tools_used: List[str] = Field(
        default_factory=list,
    )

    upstream_agents: List[str] = Field(
        default_factory=list,
    )

    downstream_agents: List[str] = Field(
        default_factory=list,
    )

    revision: int = 0

    timestamp: Optional[str] = None


class WorkflowState(BaseModel):
    """
    Central state passed through the RESONA workflow.
    """

    emergency_id: str

    situation: Optional[SituationAssessment] = None

    needs: Optional[NeedsAssessment] = None

    resources: Optional[ResourceAssessment] = None

    logistics: Optional[LogisticsAssessment] = None

    priority: Optional[PriorityAssessment] = None

    critic: Optional[CriticAssessment] = None

    final_response: Optional[ResponsePlan] = None

    agent_history: List[AgentExecutionRecord] = Field(
        default_factory=list,
    )

    revision_count: int = 0

    workflow_status: str = "initialized"
