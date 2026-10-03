"""
RESONA - Demo Emergency Scenario

Provides a realistic multi-area extreme rainfall / flooding
scenario for demonstrating the RESONA multi-agent workflow.

The scenario intentionally contains competing needs and
limited resources so that the Critic Agent can identify
potential conflicts and trigger re-evaluation.
"""

from typing import Any, Dict


DEMO_EMERGENCY_ID = "DEMO-FLOOD-001"


def get_demo_scenario() -> Dict[str, Any]:
    """
    Return the complete RESONA demonstration scenario.
    """

    return {
        "emergency_id": DEMO_EMERGENCY_ID,

        "emergency_type": (
            "Extreme Rainfall and Flooding"
        ),

        "location": (
            "Multiple affected communities"
        ),

        "severity": "high",

        "description": (
            "Heavy rainfall has caused flooding across multiple "
            "communities. Several roads are partially blocked, "
            "essential supplies are limited, and emergency teams "
            "must coordinate deployment under constrained resources."
        ),

        "affected_population": 2300,

        "affected_areas": [
            {
                "name": "Area A",
                "affected_population": 800,
                "severity": "high",
                "accessibility": "accessible",
                "critical_conditions": [
                    "High water requirement",
                    "Residential flooding",
                ],
                "notes": [
                    "Main road remains accessible."
                ],
            },
            {
                "name": "Area B",
                "affected_population": 300,
                "severity": "critical",
                "accessibility": "partially accessible",
                "critical_conditions": [
                    "Critical medical need",
                    "Limited road access",
                ],
                "notes": [
                    "Medical response requires priority consideration."
                ],
            },
            {
                "name": "Area C",
                "affected_population": 1200,
                "severity": "high",
                "accessibility": "limited",
                "critical_conditions": [
                    "Major food shortage",
                    "Limited road access",
                    "Large affected population",
                ],
                "notes": [
                    "Road access may restrict large vehicle deployment."
                ],
            },
        ],

        "available_resources": [
            {
                "name": "Food Kits",
                "category": "food",
                "quantity": 1000,
                "unit": "kits",
                "location": "Central Relief Store",
            },
            {
                "name": "Water Units",
                "category": "water",
                "quantity": 600,
                "unit": "units",
                "location": "Central Relief Store",
            },
            {
                "name": "Emergency Vehicles",
                "category": "transport",
                "quantity": 3,
                "unit": "vehicles",
                "location": "Response Base",
            },
            {
                "name": "Volunteers",
                "category": "human_resources",
                "quantity": 20,
                "unit": "people",
                "location": "Response Base",
            },
            {
                "name": "Medical Teams",
                "category": "medical",
                "quantity": 2,
                "unit": "teams",
                "location": "District Hospital",
            },
        ],

        "additional_information": [
            "Area B has an urgent medical requirement.",
            "Area C has the largest affected population.",
            "Area C has limited road accessibility.",
            "Only two medical teams are currently available.",
            "Vehicle availability is limited.",
            "Food and water supplies may not cover all estimated requirements.",
        ],

        "response_constraints": [
            "Limited transportation capacity",
            "Limited medical team availability",
            "Uneven road accessibility",
            "Finite food supplies",
            "Finite water supplies",
            "Competing humanitarian priorities",
        ],

        "expected_demo_features": [
            "Situation assessment",
            "Needs assessment",
            "Resource shortage analysis",
            "Logistics analysis",
            "Priority analysis",
            "Conflict detection",
            "Potential agent re-evaluation",
            "Final coordinated response plan",
        ],
    }


def build_demo_context() -> str:
    """
    Convert the demo scenario into a readable context string
    for the multi-agent workflow.
    """

    scenario = get_demo_scenario()

    lines = [
        "RESONA DEMONSTRATION EMERGENCY",
        "=" * 36,
        "",
        f"Emergency ID: {scenario['emergency_id']}",
        f"Emergency Type: {scenario['emergency_type']}",
        f"Location: {scenario['location']}",
        f"Severity: {scenario['severity']}",
        f"Affected Population: {scenario['affected_population']}",
        "",
        "DESCRIPTION",
        scenario["description"],
        "",
        "AFFECTED AREAS",
        "-" * 20,
    ]

    for area in scenario["affected_areas"]:

        lines.extend(
            [
                f"Area: {area['name']}",
                (
                    "Affected Population: "
                    f"{area['affected_population']}"
                ),
                f"Severity: {area['severity']}",
                (
                    "Accessibility: "
                    f"{area['accessibility']}"
                ),
                (
                    "Critical Conditions: "
                    + ", ".join(
                        area["critical_conditions"]
                    )
                ),
                (
                    "Notes: "
                    + " ".join(
                        area["notes"]
                    )
                ),
                "",
            ]
        )

    lines.extend(
        [
            "AVAILABLE RESOURCES",
            "-" * 22,
        ]
    )

    for resource in scenario[
        "available_resources"
    ]:

        lines.append(
            (
                f"- {resource['name']}: "
                f"{resource['quantity']} "
                f"{resource['unit']} "
                f"({resource['category']})"
            )
        )

    lines.extend(
        [
            "",
            "ADDITIONAL INFORMATION",
            "-" * 24,
        ]
    )

    for item in scenario[
        "additional_information"
    ]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            "RESPONSE CONSTRAINTS",
            "-" * 21,
        ]
    )

    for constraint in scenario[
        "response_constraints"
    ]:
        lines.append(
            f"- {constraint}"
        )

    lines.extend(
        [
            "",
            "IMPORTANT:",
            (
                "The agents must independently analyze the "
                "information above. Do not hardcode the final "
                "priority, allocation, or response decision."
            ),
        ]
    )

    return "\n".join(lines)


def get_demo_resource_records() -> list:
    """
    Return demo resources in a database-friendly format.
    """

    resources = []

    for index, resource in enumerate(
        get_demo_scenario()[
            "available_resources"
        ],
        start=1,
    ):
        resources.append(
            {
                "resource_id": (
                    f"DEMO-RES-{index:03d}"
                ),
                "name": resource["name"],
                "category": resource["category"],
                "quantity": resource["quantity"],
                "unit": resource["unit"],
                "location": resource["location"],
                "available": True,
                "metadata": {
                    "demo": True,
                    "emergency_id": DEMO_EMERGENCY_ID,
                },
            }
        )

    return resources
