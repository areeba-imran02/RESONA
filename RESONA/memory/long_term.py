"""
RESONA - Long-Term Memory

Provides persistent memory across emergency response sessions.

Long-term memory is backed by the RESONA SQLite database.
"""

from typing import Any, Dict, List, Optional

from memory.database import ResonaDatabase


class LongTermMemory:
    """
    Persistent memory manager for RESONA.

    This layer sits above the SQLite database and provides
    application-level methods for storing and retrieving
    reusable emergency-response knowledge.
    """

    def __init__(
        self,
        database: Optional[ResonaDatabase] = None,
    ):
        self.database = database or ResonaDatabase()

    # ========================================================
    # EMERGENCY HISTORY
    # ========================================================

    def remember_emergency(
        self,
        emergency_id: str,
        emergency_type: str,
        location: str,
        description: str = "",
        affected_population: int = 0,
        context: Optional[Dict[str, Any]] = None,
        status: str = "completed",
    ) -> None:
        """
        Store an emergency incident for future reference.
        """

        self.database.save_emergency(
            emergency_id=emergency_id,
            emergency_type=emergency_type,
            location=location,
            description=description,
            affected_population=affected_population,
            status=status,
            context=context or {},
        )

    def get_emergency_history(
        self,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent emergency incidents."""

        return self.database.get_recent_emergencies(
            limit=limit
        )

    def get_emergency(
        self,
        emergency_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a specific emergency."""

        return self.database.get_emergency(
            emergency_id
        )

    # ========================================================
    # RESPONSE PLAN MEMORY
    # ========================================================

    def remember_response_plan(
        self,
        emergency_id: str,
        response_plan: Dict[str, Any],
        confidence: str = "medium",
    ) -> int:
        """
        Store a completed response plan for future learning
        and comparison.
        """

        return self.database.save_response_plan(
            emergency_id=emergency_id,
            plan=response_plan,
            confidence=confidence,
        )

    def get_previous_response_plans(
        self,
        emergency_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve previously generated response plans.
        """

        return self.database.get_response_plans(
            emergency_id=emergency_id
        )

    # ========================================================
    # IDENTITY MEMORY
    # ========================================================

    def remember_identity(
        self,
        identity_id: str,
        identity_type: str,
        name: str = "",
        location: str = "",
        profile: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Store or update a persistent identity profile.

        Supported identity types include:
        - affected_person
        - community
        - volunteer
        - organization
        """

        self.database.save_identity(
            identity_id=identity_id,
            identity_type=identity_type,
            name=name,
            location=location,
            profile=profile or {},
        )

    def get_identity(
        self,
        identity_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a stored identity profile."""

        return self.database.get_identity(
            identity_id
        )

    # ========================================================
    # ORGANIZATION MEMORY
    # ========================================================

    def remember_organization(
        self,
        organization_id: str,
        name: str,
        location: str = "",
        service_area: Optional[List[str]] = None,
        resources: Optional[List[Dict[str, Any]]] = None,
        capacity: Optional[Dict[str, Any]] = None,
        specialization: Optional[List[str]] = None,
    ) -> None:
        """
        Store persistent information about an emergency-response
        organization.
        """

        profile = {
            "organization_id": organization_id,
            "name": name,
            "service_area": service_area or [],
            "resources": resources or [],
            "capacity": capacity or {},
            "specialization": specialization or [],
        }

        self.remember_identity(
            identity_id=organization_id,
            identity_type="organization",
            name=name,
            location=location,
            profile=profile,
        )

    def get_organization(
        self,
        organization_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve an organization profile."""

        identity = self.get_identity(
            organization_id
        )

        if not identity:
            return None

        if identity.get("identity_type") != "organization":
            return None

        return identity

    # ========================================================
    # VOLUNTEER MEMORY
    # ========================================================

    def remember_volunteer(
        self,
        volunteer_id: str,
        name: str,
        location: str = "",
        skills: Optional[List[str]] = None,
        availability: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Store persistent volunteer information.
        """

        volunteer_profile = {
            "skills": skills or [],
            "availability": availability or "unknown",
            **(profile or {}),
        }

        self.remember_identity(
            identity_id=volunteer_id,
            identity_type="volunteer",
            name=name,
            location=location,
            profile=volunteer_profile,
        )

    # ========================================================
    # RESOURCE MEMORY
    # ========================================================

    def remember_resource(
        self,
        resource_id: str,
        name: str,
        category: str,
        quantity: float = 0,
        unit: str = "",
        location: str = "",
        owner_identity_id: Optional[str] = None,
        available: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Store persistent information about an emergency resource.
        """

        self.database.save_resource(
            resource_id=resource_id,
            name=name,
            category=category,
            quantity=quantity,
            unit=unit,
            location=location,
            owner_identity_id=owner_identity_id,
            available=available,
            metadata=metadata or {},
        )

    def get_resources(
        self,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve persistent resource information."""

        return self.database.get_resources(
            category=category
        )

    # ========================================================
    # GENERAL MEMORY
    # ========================================================

    def remember(
        self,
        memory_type: str,
        memory_key: str,
        content: Dict[str, Any],
        emergency_id: Optional[str] = None,
    ) -> int:
        """
        Store a generic long-term memory.

        Example memory types:
        - organization_capability
        - volunteer_profile
        - resource_pattern
        - response_pattern
        - operational_lesson
        - emergency_pattern
        """

        return self.database.save_memory(
            memory_type=memory_type,
            memory_key=memory_key,
            content=content,
            emergency_id=emergency_id,
        )

    def recall(
        self,
        memory_type: Optional[str] = None,
        memory_key: Optional[str] = None,
        emergency_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve long-term memory records using optional filters.
        """

        return self.database.get_memories(
            memory_type=memory_type,
            memory_key=memory_key,
            emergency_id=emergency_id,
        )

    # ========================================================
    # WORKFLOW MEMORY
    # ========================================================

    def remember_agent_execution(
        self,
        emergency_id: str,
        agent_name: str,
        status: str,
        revision: int = 0,
        input_summary: str = "",
        output_summary: str = "",
        tools_used: Optional[List[str]] = None,
        upstream_agents: Optional[List[str]] = None,
        downstream_agents: Optional[List[str]] = None,
    ) -> int:
        """
        Persist an agent execution record.
        """

        return self.database.save_agent_execution(
            emergency_id=emergency_id,
            agent_name=agent_name,
            status=status,
            revision=revision,
            input_summary=input_summary,
            output_summary=output_summary,
            tools_used=tools_used or [],
            upstream_agents=upstream_agents or [],
            downstream_agents=downstream_agents or [],
        )

    def get_agent_history(
        self,
        emergency_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve persisted agent execution history."""

        return self.database.get_agent_executions(
            emergency_id=emergency_id
        )

    # ========================================================
    # WORKFLOW EVENTS
    # ========================================================

    def remember_event(
        self,
        event_type: str,
        message: str,
        emergency_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Persist an important workflow event."""

        return self.database.log_event(
            event_type=event_type,
            message=message,
            emergency_id=emergency_id,
            agent_name=agent_name,
            metadata=metadata or {},
        )

    def get_events(
        self,
        emergency_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve persisted workflow events."""

        return self.database.get_events(
            emergency_id=emergency_id
        )

    # ========================================================
    # CONTEXT FOR NEW EMERGENCY
    # ========================================================

    def build_context_for_new_emergency(
        self,
        emergency_type: str,
        location: str,
    ) -> Dict[str, Any]:
        """
        Retrieve useful historical information before starting
        a new emergency workflow.

        This does not make decisions. It provides historical
        context that agents can consider alongside current data.
        """

        previous_emergencies = (
            self.get_emergency_history(limit=10)
        )

        previous_plans = (
            self.get_previous_response_plans()
        )

        organizations = self.recall(
            memory_type="organization_capability"
        )

        resource_patterns = self.recall(
            memory_type="resource_pattern"
        )

        emergency_patterns = self.recall(
            memory_type="emergency_pattern"
        )

        return {
            "current_emergency_type": emergency_type,
            "current_location": location,
            "previous_emergencies": previous_emergencies,
            "previous_response_plans": previous_plans[:10],
            "organization_capabilities": organizations[:20],
            "resource_patterns": resource_patterns[:20],
            "similar_emergency_patterns": emergency_patterns[:20],
        }

    # ========================================================
    # MEMORY SUMMARY
    # ========================================================

    def summary(self) -> Dict[str, Any]:
        """
        Return a compact summary of persistent memory.
        """

        emergencies = self.get_emergency_history(
            limit=100
        )

        resources = self.get_resources()

        organizations = self.recall(
            memory_type="organization_capability"
        )

        volunteers = self.database.get_memories(
            memory_type="volunteer_profile"
        )

        response_plans = (
            self.get_previous_response_plans()
        )

        return {
            "emergency_count": len(emergencies),
            "resource_count": len(resources),
            "organization_memory_count": len(
                organizations
            ),
            "volunteer_memory_count": len(
                volunteers
            ),
            "response_plan_count": len(
                response_plans
            ),
        }
