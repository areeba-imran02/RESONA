"""
RESONA - Identity Manager

Manages operational identity profiles for people,
volunteers, organizations, and affected communities.

This module is NOT a biometric identification system.

It answers operational questions such as:
- Who is involved?
- Where are they located?
- What do they need?
- What can they provide?
- What skills or resources are available?
- What is their current emergency-response status?

Persistent identity data is stored through the RESONA
SQLite database layer.
"""

from typing import Any, Dict, List, Optional

from memory.database import ResonaDatabase


# ============================================================
# IDENTITY TYPES
# ============================================================

IDENTITY_TYPE_AFFECTED_PERSON = "affected_person"
IDENTITY_TYPE_COMMUNITY = "community"
IDENTITY_TYPE_VOLUNTEER = "volunteer"
IDENTITY_TYPE_ORGANIZATION = "organization"


VALID_IDENTITY_TYPES = {
    IDENTITY_TYPE_AFFECTED_PERSON,
    IDENTITY_TYPE_COMMUNITY,
    IDENTITY_TYPE_VOLUNTEER,
    IDENTITY_TYPE_ORGANIZATION,
}


# ============================================================
# IDENTITY MANAGER
# ============================================================

class IdentityManager:
    """
    Central manager for RESONA operational identities.

    The manager provides a consistent interface for creating,
    updating, retrieving, and searching identity profiles.
    """

    def __init__(
        self,
        database: Optional[ResonaDatabase] = None,
    ):
        self.database = database or ResonaDatabase()

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def _validate_identity_type(
        identity_type: str,
    ) -> None:
        """
        Validate an identity type.
        """

        if identity_type not in VALID_IDENTITY_TYPES:
            allowed = ", ".join(
                sorted(VALID_IDENTITY_TYPES)
            )

            raise ValueError(
                f"Invalid identity type '{identity_type}'. "
                f"Allowed types: {allowed}"
            )

    @staticmethod
    def _validate_identity_id(
        identity_id: str,
    ) -> None:
        """
        Validate an identity identifier.
        """

        if not identity_id or not identity_id.strip():
            raise ValueError(
                "Identity ID cannot be empty."
            )

    # ========================================================
    # CREATE / UPDATE
    # ========================================================

    def create_identity(
        self,
        identity_id: str,
        identity_type: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create or update an operational identity profile.
        """

        self._validate_identity_id(
            identity_id
        )

        self._validate_identity_type(
            identity_type
        )

        profile_data = dict(
            profile or {}
        )

        self.database.save_identity(
            identity_id=identity_id.strip(),
            identity_type=identity_type,
            name=name,
            location=location,
            profile=profile_data,
        )

        return {
            "success": True,
            "identity_id": identity_id.strip(),
            "identity_type": identity_type,
            "name": name,
            "location": location,
            "profile": profile_data,
        }

    # ========================================================
    # AFFECTED PERSON / COMMUNITY
    # ========================================================

    def register_affected_person(
        self,
        identity_id: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        household_size: Optional[int] = None,
        reported_needs: Optional[List[str]] = None,
        status: str = "affected",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register an affected person or household.
        """

        profile = {
            "household_size": household_size,
            "reported_needs": reported_needs or [],
            "status": status,
            "context": context or {},
        }

        return self.create_identity(
            identity_id=identity_id,
            identity_type=IDENTITY_TYPE_AFFECTED_PERSON,
            name=name,
            location=location,
            profile=profile,
        )

    def register_community(
        self,
        identity_id: str,
        name: str,
        location: Optional[str] = None,
        affected_population: int = 0,
        reported_needs: Optional[List[str]] = None,
        status: str = "affected",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register an affected community or area profile.
        """

        if affected_population < 0:
            raise ValueError(
                "Affected population cannot be negative."
            )

        profile = {
            "affected_population": affected_population,
            "reported_needs": reported_needs or [],
            "status": status,
            "context": context or {},
        }

        return self.create_identity(
            identity_id=identity_id,
            identity_type=IDENTITY_TYPE_COMMUNITY,
            name=name,
            location=location,
            profile=profile,
        )

    # ========================================================
    # VOLUNTEERS
    # ========================================================

    def register_volunteer(
        self,
        identity_id: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        skills: Optional[List[str]] = None,
        availability: str = "available",
        assigned_task: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a volunteer profile.
        """

        profile = {
            "skills": skills or [],
            "availability": availability,
            "assigned_task": assigned_task,
            "context": context or {},
        }

        result = self.create_identity(
            identity_id=identity_id,
            identity_type=IDENTITY_TYPE_VOLUNTEER,
            name=name,
            location=location,
            profile=profile,
        )

        return result

    # ========================================================
    # ORGANIZATIONS
    # ========================================================

    def register_organization(
        self,
        identity_id: str,
        name: str,
        location: Optional[str] = None,
        service_area: Optional[str] = None,
        resources: Optional[List[str]] = None,
        capacity: Optional[str] = None,
        specialization: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register an organization participating in
        emergency response.
        """

        profile = {
            "service_area": service_area,
            "resources": resources or [],
            "capacity": capacity,
            "specialization": specialization or [],
            "context": context or {},
        }

        return self.create_identity(
            identity_id=identity_id,
            identity_type=IDENTITY_TYPE_ORGANIZATION,
            name=name,
            location=location,
            profile=profile,
        )

    # ========================================================
    # RETRIEVAL
    # ========================================================

    def get_identity(
        self,
        identity_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve one identity profile.
        """

        self._validate_identity_id(
            identity_id
        )

        return self.database.get_identity(
            identity_id
        )

    def get_volunteer(
        self,
        identity_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a volunteer and verify its identity type.
        """

        identity = self.get_identity(
            identity_id
        )

        if not identity:
            return None

        if identity.get(
            "identity_type"
        ) != IDENTITY_TYPE_VOLUNTEER:
            return None

        return identity

    def get_organization(
        self,
        identity_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve an organization and verify its identity type.
        """

        identity = self.get_identity(
            identity_id
        )

        if not identity:
            return None

        if identity.get(
            "identity_type"
        ) != IDENTITY_TYPE_ORGANIZATION:
            return None

        return identity

    # ========================================================
    # SEARCH
    # ========================================================

    def find_identities(
        self,
        identity_type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search stored identities.

        The database layer currently provides direct identity
        retrieval. This method performs filtering on the
        retrieved records so the UI and workflow can use a
        simple search interface.
        """

        if identity_type:
            self._validate_identity_type(
                identity_type
            )

        results: List[Dict[str, Any]] = []

        # SQLite database currently exposes direct identity
        # retrieval rather than a generic identity listing API.
        # Use the database connection directly for controlled
        # read-only filtering.
        connection = self.database._get_connection()

        try:
            cursor = connection.cursor()

            query = """
                SELECT
                    identity_id,
                    identity_type,
                    name,
                    location,
                    profile_json,
                    created_at,
                    updated_at
                FROM identities
                WHERE 1 = 1
            """

            parameters: List[Any] = []

            if identity_type:
                query += """
                    AND identity_type = ?
                """

                parameters.append(
                    identity_type
                )

            if location:
                query += """
                    AND LOWER(location) LIKE LOWER(?)
                """

                parameters.append(
                    f"%{location}%"
                )

            query += """
                ORDER BY updated_at DESC
            """

            cursor.execute(
                query,
                parameters,
            )

            rows = cursor.fetchall()

            for row in rows:
                result = dict(row)

                profile_json = result.get(
                    "profile_json"
                )

                if profile_json:
                    try:
                        import json

                        result["profile"] = (
                            json.loads(profile_json)
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):
                        result["profile"] = {}

                else:
                    result["profile"] = {}

                results.append(
                    result
                )

        finally:
            connection.close()

        return results

    # ========================================================
    # OPERATIONAL CONTEXT
    # ========================================================

    def build_identity_context(
        self,
        identity_ids: List[str],
    ) -> str:
        """
        Build concise identity context for agent workflows.

        Sensitive or unnecessary information should not be added
        to the agent context. Only operationally relevant fields
        are included.
        """

        if not identity_ids:
            return (
                "No identity profiles were provided."
            )

        context_lines = [
            "IDENTITY / PARTICIPANT CONTEXT"
        ]

        for identity_id in identity_ids:

            identity = self.get_identity(
                identity_id
            )

            if not identity:
                context_lines.append(
                    f"- {identity_id}: profile not found"
                )
                continue

            identity_type = identity.get(
                "identity_type",
                "unknown",
            )

            name = identity.get(
                "name",
                "Unnamed",
            )

            location = identity.get(
                "location",
                "Unknown location",
            )

            context_lines.append(
                f"- ID: {identity.get('identity_id', identity_id)}"
            )

            context_lines.append(
                f"  Type: {identity_type}"
            )

            context_lines.append(
                f"  Name: {name}"
            )

            context_lines.append(
                f"  Location: {location}"
            )

            profile = identity.get(
                "profile",
                {},
            )

            if identity_type == IDENTITY_TYPE_VOLUNTEER:

                skills = profile.get(
                    "skills",
                    [],
                )

                availability = profile.get(
                    "availability",
                    "unknown",
                )

                context_lines.append(
                    f"  Skills: {', '.join(skills) if skills else 'Not provided'}"
                )

                context_lines.append(
                    f"  Availability: {availability}"
                )

                assigned_task = profile.get(
                    "assigned_task"
                )

                if assigned_task:
                    context_lines.append(
                        f"  Assigned task: {assigned_task}"
                    )

            elif identity_type == IDENTITY_TYPE_ORGANIZATION:

                service_area = profile.get(
                    "service_area"
                )

                if service_area:
                    context_lines.append(
                        f"  Service area: {service_area}"
                    )

                specialization = profile.get(
                    "specialization",
                    [],
                )

                context_lines.append(
                    "  Specialization: "
                    + (
                        ", ".join(specialization)
                        if specialization
                        else "Not provided"
                    )
                )

                resources = profile.get(
                    "resources",
                    [],
                )

                context_lines.append(
                    "  Resources: "
                    + (
                        ", ".join(resources)
                        if resources
                        else "Not provided"
                    )
                )

            elif identity_type == IDENTITY_TYPE_AFFECTED_PERSON:

                household_size = profile.get(
                    "household_size"
                )

                if household_size is not None:
                    context_lines.append(
                        f"  Household size: {household_size}"
                    )

                needs = profile.get(
                    "reported_needs",
                    [],
                )

                context_lines.append(
                    "  Reported needs: "
                    + (
                        ", ".join(needs)
                        if needs
                        else "Not provided"
                    )
                )

                status = profile.get(
                    "status",
                    "unknown",
                )

                context_lines.append(
                    f"  Status: {status}"
                )

            elif identity_type == IDENTITY_TYPE_COMMUNITY:

                population = profile.get(
                    "affected_population",
                    0,
                )

                needs = profile.get(
                    "reported_needs",
                    [],
                )

                context_lines.append(
                    f"  Affected population: {population}"
                )

                context_lines.append(
                    "  Reported needs: "
                    + (
                        ", ".join(needs)
                        if needs
                        else "Not provided"
                    )
                )

        return "\n".join(
            context_lines
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    def summary(self) -> Dict[str, Any]:
        """
        Return a high-level summary of stored identities.
        """

        all_identities = self.find_identities()

        summary = {
            "total": len(
                all_identities
            ),
            "affected_people": 0,
            "communities": 0,
            "volunteers": 0,
            "organizations": 0,
        }

        for identity in all_identities:

            identity_type = identity.get(
                "identity_type"
            )

            if identity_type == IDENTITY_TYPE_AFFECTED_PERSON:
                summary["affected_people"] += 1

            elif identity_type == IDENTITY_TYPE_COMMUNITY:
                summary["communities"] += 1

            elif identity_type == IDENTITY_TYPE_VOLUNTEER:
                summary["volunteers"] += 1

            elif identity_type == IDENTITY_TYPE_ORGANIZATION:
                summary["organizations"] += 1

        return summary
