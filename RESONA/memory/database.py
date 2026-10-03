"""
RESONA - Database Manager

Provides the SQLite database layer used by RESONA's
short-term and long-term memory systems.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config.settings import DATABASE_FILE


class ResonaDatabase:
    """
    Central SQLite database manager for RESONA.

    The database stores:
    - Emergency incidents
    - Agent execution records
    - Response plans
    - People and organizations
    - Resources
    - Workflow memory
    """

    def __init__(self, database_path: Optional[str] = None):
        self.database_path = database_path or DATABASE_FILE

        self._ensure_database_directory()
        self._initialize_database()

    # ========================================================
    # DATABASE SETUP
    # ========================================================

    def _ensure_database_directory(self) -> None:
        """Create the database directory if it does not exist."""

        directory = os.path.dirname(self.database_path)

        if directory:
            os.makedirs(directory, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """
        Create a SQLite connection with row access by column name.
        """

        connection = sqlite3.connect(self.database_path)

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize_database(self) -> None:
        """
        Create all required RESONA database tables.
        """

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            # ------------------------------------------------
            # Emergency incidents
            # ------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS emergencies (
                    emergency_id TEXT PRIMARY KEY,
                    emergency_type TEXT NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT,
                    affected_population INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    context_json TEXT
                )
                """
            )

            # ------------------------------------------------
            # Agent execution history
            # ------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emergency_id TEXT,
                    agent_name TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    revision INTEGER DEFAULT 0,
                    input_summary TEXT,
                    output_summary TEXT,
                    tools_used_json TEXT,
                    upstream_agents_json TEXT,
                    downstream_agents_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (emergency_id)
                        REFERENCES emergencies(emergency_id)
                )
                """
            )

            # ------------------------------------------------
            # Response plans
            # ------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS response_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emergency_id TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    confidence TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (emergency_id)
                        REFERENCES emergencies(emergency_id)
                )
                """
            )

            # ------------------------------------------------
            # People / identity profiles
            # ------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS identities (
                    identity_id TEXT PRIMARY KEY,
                    identity_type TEXT NOT NULL,
                    name TEXT,
                    location TEXT,
                    profile_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            # ------------------------------------------------
            # Resources
            # ------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS resources (
                    resource_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    quantity REAL DEFAULT 0,
                    unit TEXT,
                    location TEXT,
                    owner_identity_id TEXT,
                    available INTEGER DEFAULT 1,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            # ------------------------------------------------
            # Long-term memory records
            # ------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT NOT NULL,
                    memory_key TEXT NOT NULL,
                    content_json TEXT NOT NULL,
                    emergency_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            # ------------------------------------------------
            # Workflow events
            # ------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emergency_id TEXT,
                    event_type TEXT NOT NULL,
                    agent_name TEXT,
                    message TEXT,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.commit()

        finally:
            connection.close()

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _now() -> str:
        """Return the current UTC timestamp."""

        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _json_dumps(value: Any) -> str:
        """Safely convert Python data to JSON."""

        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _json_loads(value: Optional[str]) -> Any:
        """Safely convert JSON text back to Python data."""

        if not value:
            return None

        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return value

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a SQLite row into a normal dictionary."""

        return dict(row)

    # ========================================================
    # EMERGENCIES
    # ========================================================

    def save_emergency(
        self,
        emergency_id: str,
        emergency_type: str,
        location: str,
        description: str = "",
        affected_population: int = 0,
        status: str = "active",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Create or update an emergency incident.
        """

        now = self._now()

        connection = self._get_connection()

        try:
            connection.execute(
                """
                INSERT INTO emergencies (
                    emergency_id,
                    emergency_type,
                    location,
                    description,
                    affected_population,
                    status,
                    created_at,
                    updated_at,
                    context_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(emergency_id)
                DO UPDATE SET
                    emergency_type = excluded.emergency_type,
                    location = excluded.location,
                    description = excluded.description,
                    affected_population = excluded.affected_population,
                    status = excluded.status,
                    updated_at = excluded.updated_at,
                    context_json = excluded.context_json
                """,
                (
                    emergency_id,
                    emergency_type,
                    location,
                    description,
                    affected_population,
                    status,
                    now,
                    now,
                    self._json_dumps(context or {}),
                ),
            )

            connection.commit()

        finally:
            connection.close()

    def get_emergency(
        self,
        emergency_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve one emergency by ID."""

        connection = self._get_connection()

        try:
            row = connection.execute(
                """
                SELECT *
                FROM emergencies
                WHERE emergency_id = ?
                """,
                (emergency_id,),
            ).fetchone()

            if row is None:
                return None

            result = self._row_to_dict(row)

            result["context"] = self._json_loads(
                result.pop("context_json", None)
            )

            return result

        finally:
            connection.close()

    def get_recent_emergencies(
        self,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Return recent emergency incidents."""

        connection = self._get_connection()

        try:
            rows = connection.execute(
                """
                SELECT *
                FROM emergencies
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            results = []

            for row in rows:
                result = self._row_to_dict(row)

                result["context"] = self._json_loads(
                    result.pop("context_json", None)
                )

                results.append(result)

            return results

        finally:
            connection.close()

    # ========================================================
    # AGENT EXECUTIONS
    # ========================================================

    def save_agent_execution(
        self,
        emergency_id: Optional[str],
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
        Store an agent execution record.
        """

        connection = self._get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO agent_executions (
                    emergency_id,
                    agent_name,
                    status,
                    revision,
                    input_summary,
                    output_summary,
                    tools_used_json,
                    upstream_agents_json,
                    downstream_agents_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    emergency_id,
                    agent_name,
                    status,
                    revision,
                    input_summary,
                    output_summary,
                    self._json_dumps(tools_used or []),
                    self._json_dumps(upstream_agents or []),
                    self._json_dumps(downstream_agents or []),
                    self._now(),
                ),
            )

            connection.commit()

            return int(cursor.lastrowid)

        finally:
            connection.close()

    def get_agent_executions(
        self,
        emergency_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve agent execution history."""

        connection = self._get_connection()

        try:
            if emergency_id:

                rows = connection.execute(
                    """
                    SELECT *
                    FROM agent_executions
                    WHERE emergency_id = ?
                    ORDER BY created_at ASC
                    """,
                    (emergency_id,),
                ).fetchall()

            else:

                rows = connection.execute(
                    """
                    SELECT *
                    FROM agent_executions
                    ORDER BY created_at DESC
                    """
                ).fetchall()

            results = []

            for row in rows:
                result = self._row_to_dict(row)

                result["tools_used"] = self._json_loads(
                    result.pop("tools_used_json", None)
                )

                result["upstream_agents"] = self._json_loads(
                    result.pop("upstream_agents_json", None)
                )

                result["downstream_agents"] = self._json_loads(
                    result.pop("downstream_agents_json", None)
                )

                results.append(result)

            return results

        finally:
            connection.close()

    # ========================================================
    # RESPONSE PLANS
    # ========================================================

    def save_response_plan(
        self,
        emergency_id: str,
        plan: Dict[str, Any],
        confidence: str = "medium",
    ) -> int:
        """Store a final coordinated response plan."""

        connection = self._get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO response_plans (
                    emergency_id,
                    plan_json,
                    confidence,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    emergency_id,
                    self._json_dumps(plan),
                    confidence,
                    self._now(),
                ),
            )

            connection.commit()

            return int(cursor.lastrowid)

        finally:
            connection.close()

    def get_response_plans(
        self,
        emergency_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve stored response plans."""

        connection = self._get_connection()

        try:
            if emergency_id:

                rows = connection.execute(
                    """
                    SELECT *
                    FROM response_plans
                    WHERE emergency_id = ?
                    ORDER BY created_at DESC
                    """,
                    (emergency_id,),
                ).fetchall()

            else:

                rows = connection.execute(
                    """
                    SELECT *
                    FROM response_plans
                    ORDER BY created_at DESC
                    """
                ).fetchall()

            results = []

            for row in rows:
                result = self._row_to_dict(row)

                result["plan"] = self._json_loads(
                    result.pop("plan_json", None)
                )

                results.append(result)

            return results

        finally:
            connection.close()

    # ========================================================
    # IDENTITY MEMORY
    # ========================================================

    def save_identity(
        self,
        identity_id: str,
        identity_type: str,
        name: str = "",
        location: str = "",
        profile: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create or update an identity profile."""

        now = self._now()

        connection = self._get_connection()

        try:
            connection.execute(
                """
                INSERT INTO identities (
                    identity_id,
                    identity_type,
                    name,
                    location,
                    profile_json,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(identity_id)
                DO UPDATE SET
                    identity_type = excluded.identity_type,
                    name = excluded.name,
                    location = excluded.location,
                    profile_json = excluded.profile_json,
                    updated_at = excluded.updated_at
                """,
                (
                    identity_id,
                    identity_type,
                    name,
                    location,
                    self._json_dumps(profile or {}),
                    now,
                    now,
                ),
            )

            connection.commit()

        finally:
            connection.close()

    def get_identity(
        self,
        identity_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve an identity profile."""

        connection = self._get_connection()

        try:
            row = connection.execute(
                """
                SELECT *
                FROM identities
                WHERE identity_id = ?
                """,
                (identity_id,),
            ).fetchone()

            if row is None:
                return None

            result = self._row_to_dict(row)

            result["profile"] = self._json_loads(
                result.pop("profile_json", None)
            )

            return result

        finally:
            connection.close()

    # ========================================================
    # RESOURCE MEMORY
    # ========================================================

    def save_resource(
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
        """Create or update a resource record."""

        now = self._now()

        connection = self._get_connection()

        try:
            connection.execute(
                """
                INSERT INTO resources (
                    resource_id,
                    name,
                    category,
                    quantity,
                    unit,
                    location,
                    owner_identity_id,
                    available,
                    metadata_json,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(resource_id)
                DO UPDATE SET
                    name = excluded.name,
                    category = excluded.category,
                    quantity = excluded.quantity,
                    unit = excluded.unit,
                    location = excluded.location,
                    owner_identity_id = excluded.owner_identity_id,
                    available = excluded.available,
                    metadata_json = excluded.metadata_json,
                    updated_at = excluded.updated_at
                """,
                (
                    resource_id,
                    name,
                    category,
                    quantity,
                    unit,
                    location,
                    owner_identity_id,
                    int(available),
                    self._json_dumps(metadata or {}),
                    now,
                    now,
                ),
            )

            connection.commit()

        finally:
            connection.close()

    def get_resources(
        self,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve resource records."""

        connection = self._get_connection()

        try:
            if category:

                rows = connection.execute(
                    """
                    SELECT *
                    FROM resources
                    WHERE category = ?
                    ORDER BY name ASC
                    """,
                    (category,),
                ).fetchall()

            else:

                rows = connection.execute(
                    """
                    SELECT *
                    FROM resources
                    ORDER BY name ASC
                    """
                ).fetchall()

            results = []

            for row in rows:
                result = self._row_to_dict(row)

                result["available"] = bool(
                    result["available"]
                )

                result["metadata"] = self._json_loads(
                    result.pop("metadata_json", None)
                )

                results.append(result)

            return results

        finally:
            connection.close()

    # ========================================================
    # LONG-TERM MEMORY
    # ========================================================

    def save_memory(
        self,
        memory_type: str,
        memory_key: str,
        content: Dict[str, Any],
        emergency_id: Optional[str] = None,
    ) -> int:
        """
        Store a long-term memory record.
        """

        now = self._now()

        connection = self._get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO memory_records (
                    memory_type,
                    memory_key,
                    content_json,
                    emergency_id,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_type,
                    memory_key,
                    self._json_dumps(content),
                    emergency_id,
                    now,
                    now,
                ),
            )

            connection.commit()

            return int(cursor.lastrowid)

        finally:
            connection.close()

    def get_memories(
        self,
        memory_type: Optional[str] = None,
        memory_key: Optional[str] = None,
        emergency_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve long-term memory records."""

        connection = self._get_connection()

        try:
            conditions = []
            parameters = []

            if memory_type:
                conditions.append("memory_type = ?")
                parameters.append(memory_type)

            if memory_key:
                conditions.append("memory_key = ?")
                parameters.append(memory_key)

            if emergency_id:
                conditions.append("emergency_id = ?")
                parameters.append(emergency_id)

            query = """
                SELECT *
                FROM memory_records
            """

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY updated_at DESC"

            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

            results = []

            for row in rows:
                result = self._row_to_dict(row)

                result["content"] = self._json_loads(
                    result.pop("content_json", None)
                )

                results.append(result)

            return results

        finally:
            connection.close()

    # ========================================================
    # WORKFLOW EVENTS
    # ========================================================

    def log_event(
        self,
        event_type: str,
        message: str,
        emergency_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Store a workflow event."""

        connection = self._get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO workflow_events (
                    emergency_id,
                    event_type,
                    agent_name,
                    message,
                    metadata_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    emergency_id,
                    event_type,
                    agent_name,
                    message,
                    self._json_dumps(metadata or {}),
                    self._now(),
                ),
            )

            connection.commit()

            return int(cursor.lastrowid)

        finally:
            connection.close()

    def get_events(
        self,
        emergency_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve workflow events."""

        connection = self._get_connection()

        try:
            if emergency_id:

                rows = connection.execute(
                    """
                    SELECT *
                    FROM workflow_events
                    WHERE emergency_id = ?
                    ORDER BY created_at ASC
                    """,
                    (emergency_id,),
                ).fetchall()

            else:

                rows = connection.execute(
                    """
                    SELECT *
                    FROM workflow_events
                    ORDER BY created_at DESC
                    """
                ).fetchall()

            results = []

            for row in rows:
                result = self._row_to_dict(row)

                result["metadata"] = self._json_loads(
                    result.pop("metadata_json", None)
                )

                results.append(result)

            return results

        finally:
            connection.close()
