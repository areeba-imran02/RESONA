"""
RESONA - Short-Term Memory

Stores and manages the active workflow state for the
current emergency response session.
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional

from crew.schemas import WorkflowState


class ShortTermMemory:
    """
    In-memory working state for one RESONA emergency workflow.

    Short-term memory is intentionally session-focused.
    Long-term persistence is handled separately by the
    SQLite-based long-term memory layer.
    """

    def __init__(self, emergency_id: str):
        if not emergency_id or not emergency_id.strip():
            raise ValueError(
                "emergency_id is required for short-term memory."
            )

        self.emergency_id = emergency_id.strip()

        self._state: Dict[str, Any] = {
            "emergency_id": self.emergency_id,
            "workflow_status": "initialized",
            "revision_count": 0,
            "situation": None,
            "needs": None,
            "resources": None,
            "logistics": None,
            "priority": None,
            "critic": None,
            "final_response": None,
            "agent_history": [],
            "context": {},
            "conflicts": [],
            "decisions": [],
            "events": [],
        }

    # ========================================================
    # STATE
    # ========================================================

    def set_workflow_status(self, status: str) -> None:
        """Update the current workflow status."""

        self._state["workflow_status"] = status

    def get_workflow_status(self) -> str:
        """Return the current workflow status."""

        return self._state.get(
            "workflow_status",
            "initialized",
        )

    def increment_revision(self) -> int:
        """Increase the workflow revision count."""

        self._state["revision_count"] += 1

        return self._state["revision_count"]

    def get_revision_count(self) -> int:
        """Return the current revision count."""

        return int(
            self._state.get(
                "revision_count",
                0,
            )
        )

    # ========================================================
    # CONTEXT
    # ========================================================

    def set_context(
        self,
        context: Dict[str, Any],
    ) -> None:
        """Store the current emergency context."""

        self._state["context"] = deepcopy(
            context or {}
        )

    def update_context(
        self,
        updates: Dict[str, Any],
    ) -> None:
        """Update selected emergency context fields."""

        if not isinstance(updates, dict):
            raise TypeError(
                "Context updates must be a dictionary."
            )

        self._state["context"].update(
            deepcopy(updates)
        )

    def get_context(self) -> Dict[str, Any]:
        """Return a copy of the current emergency context."""

        return deepcopy(
            self._state.get(
                "context",
                {},
            )
        )

    # ========================================================
    # AGENT OUTPUTS
    # ========================================================

    def set_agent_output(
        self,
        agent_key: str,
        output: Any,
    ) -> None:
        """
        Store the latest structured output produced by an agent.

        Examples of agent_key:
        - situation
        - needs
        - resources
        - logistics
        - priority
        - critic
        - final_response
        """

        if not agent_key or not agent_key.strip():
            raise ValueError(
                "agent_key cannot be empty."
            )

        self._state[agent_key.strip()] = deepcopy(
            output
        )

    def get_agent_output(
        self,
        agent_key: str,
    ) -> Any:
        """Retrieve the latest output of an agent."""

        return deepcopy(
            self._state.get(
                agent_key,
            )
        )

    def has_agent_output(
        self,
        agent_key: str,
    ) -> bool:
        """Check whether an agent has produced an output."""

        return self._state.get(agent_key) is not None

    # ========================================================
    # AGENT HISTORY
    # ========================================================

    def add_agent_history(
        self,
        record: Dict[str, Any],
    ) -> None:
        """Add an execution record to the current workflow."""

        if not isinstance(record, dict):
            raise TypeError(
                "Agent history record must be a dictionary."
            )

        self._state["agent_history"].append(
            deepcopy(record)
        )

    def get_agent_history(self) -> List[Dict[str, Any]]:
        """Return the current agent execution history."""

        return deepcopy(
            self._state.get(
                "agent_history",
                [],
            )
        )

    # ========================================================
    # CONFLICTS
    # ========================================================

    def add_conflict(
        self,
        conflict: Dict[str, Any],
    ) -> None:
        """Add a detected conflict to short-term memory."""

        if not isinstance(conflict, dict):
            raise TypeError(
                "Conflict must be a dictionary."
            )

        self._state["conflicts"].append(
            deepcopy(conflict)
        )

    def set_conflicts(
        self,
        conflicts: List[Dict[str, Any]],
    ) -> None:
        """Replace the current conflict list."""

        self._state["conflicts"] = deepcopy(
            conflicts or []
        )

    def get_conflicts(self) -> List[Dict[str, Any]]:
        """Return all conflicts detected during the workflow."""

        return deepcopy(
            self._state.get(
                "conflicts",
                [],
            )
        )

    # ========================================================
    # DECISIONS
    # ========================================================

    def add_decision(
        self,
        decision: Dict[str, Any],
    ) -> None:
        """
        Store an important workflow decision.

        Decisions can include:
        - resource allocation
        - priority adjustment
        - agent re-evaluation
        - conflict resolution
        - final coordination decision
        """

        if not isinstance(decision, dict):
            raise TypeError(
                "Decision must be a dictionary."
            )

        self._state["decisions"].append(
            deepcopy(decision)
        )

    def get_decisions(self) -> List[Dict[str, Any]]:
        """Return decisions made during the current workflow."""

        return deepcopy(
            self._state.get(
                "decisions",
                [],
            )
        )

    # ========================================================
    # EVENTS
    # ========================================================

    def add_event(
        self,
        event: Dict[str, Any],
    ) -> None:
        """Store a workflow event in current memory."""

        if not isinstance(event, dict):
            raise TypeError(
                "Event must be a dictionary."
            )

        self._state["events"].append(
            deepcopy(event)
        )

    def get_events(self) -> List[Dict[str, Any]]:
        """Return current workflow events."""

        return deepcopy(
            self._state.get(
                "events",
                [],
            )
        )

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def get_snapshot(self) -> Dict[str, Any]:
        """
        Return a complete copy of the current short-term memory.

        The returned dictionary can safely be passed to UI,
        persistence, logging, or workflow components.
        """

        return deepcopy(self._state)

    # ========================================================
    # WORKFLOW STATE
    # ========================================================

    def to_workflow_state(self) -> WorkflowState:
        """
        Convert the current short-term memory into the shared
        WorkflowState Pydantic model.

        Structured agent outputs are accepted when they are
        already Pydantic models or dictionaries compatible with
        the corresponding schema.
        """

        state_data = {
            "emergency_id": self.emergency_id,
            "situation": self._state.get("situation"),
            "needs": self._state.get("needs"),
            "resources": self._state.get("resources"),
            "logistics": self._state.get("logistics"),
            "priority": self._state.get("priority"),
            "critic": self._state.get("critic"),
            "final_response": self._state.get(
                "final_response"
            ),
            "agent_history": self._state.get(
                "agent_history",
                [],
            ),
            "revision_count": self._state.get(
                "revision_count",
                0,
            ),
            "workflow_status": self._state.get(
                "workflow_status",
                "initialized",
            ),
        }

        return WorkflowState.model_validate(
            state_data
        )

    # ========================================================
    # CLEAR / RESET
    # ========================================================

    def clear(self) -> None:
        """
        Reset the current short-term memory while preserving
        the emergency ID.
        """

        self._state = {
            "emergency_id": self.emergency_id,
            "workflow_status": "initialized",
            "revision_count": 0,
            "situation": None,
            "needs": None,
            "resources": None,
            "logistics": None,
            "priority": None,
            "critic": None,
            "final_response": None,
            "agent_history": [],
            "context": {},
            "conflicts": [],
            "decisions": [],
            "events": [],
        }

    # ========================================================
    # SUMMARY
    # ========================================================

    def summary(self) -> Dict[str, Any]:
        """
        Return a compact summary useful for the UI.
        """

        completed_agents = []

        for record in self._state.get(
            "agent_history",
            [],
        ):
            if record.get("status") == "completed":
                completed_agents.append(
                    record.get("agent_name")
                )

        return {
            "emergency_id": self.emergency_id,
            "workflow_status": self.get_workflow_status(),
            "revision_count": self.get_revision_count(),
            "completed_agents": completed_agents,
            "conflict_count": len(
                self._state.get(
                    "conflicts",
                    [],
                )
            ),
            "decision_count": len(
                self._state.get(
                    "decisions",
                    [],
                )
            ),
            "event_count": len(
                self._state.get(
                    "events",
                    [],
                )
            ),
            "has_final_response": self.has_agent_output(
                "final_response"
            ),
        }
