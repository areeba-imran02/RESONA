"""
RESONA - Calculator Tool

Provides deterministic calculations for emergency-response
resource planning and analysis.

The tool performs mathematical operations only. It does not
make emergency decisions by itself.
"""

from typing import Dict, Optional


# ============================================================
# BASIC CALCULATIONS
# ============================================================

def calculate_shortage(
    required: float,
    available: float,
) -> Dict[str, float]:
    """
    Calculate the shortage between required and available
    resources.

    Example:
        required = 1000
        available = 600

        shortage = 400
    """

    required = max(float(required), 0.0)
    available = max(float(available), 0.0)

    shortage = max(required - available, 0.0)
    surplus = max(available - required, 0.0)

    return {
        "required": required,
        "available": available,
        "shortage": shortage,
        "surplus": surplus,
    }


def calculate_coverage_percentage(
    required: float,
    available: float,
) -> float:
    """
    Calculate how much of a requirement can be covered
    by available resources.

    Result is capped at 100%.
    """

    required = float(required)
    available = max(float(available), 0.0)

    if required <= 0:
        return 100.0

    percentage = (
        available / required
    ) * 100.0

    return round(
        min(max(percentage, 0.0), 100.0),
        2,
    )


def calculate_allocation_percentage(
    allocation: float,
    total_available: float,
) -> float:
    """
    Calculate what percentage of the total available
    resource is being allocated.
    """

    allocation = max(float(allocation), 0.0)
    total_available = float(total_available)

    if total_available <= 0:
        return 0.0

    percentage = (
        allocation / total_available
    ) * 100.0

    return round(
        min(max(percentage, 0.0), 100.0),
        2,
    )


def calculate_remaining_resource(
    total_available: float,
    allocated: float,
) -> float:
    """
    Calculate the resource remaining after allocation.
    """

    total_available = max(
        float(total_available),
        0.0,
    )

    allocated = max(
        float(allocated),
        0.0,
    )

    return max(
        total_available - allocated,
        0.0,
    )


# ============================================================
# PRIORITY CALCULATIONS
# ============================================================

def calculate_priority_score(
    population_impact: float = 0.0,
    severity: float = 0.0,
    urgency: float = 0.0,
    vulnerability: float = 0.0,
    resource_shortage: float = 0.0,
    accessibility_constraint: float = 0.0,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Calculate a transparent priority score.

    Each factor is expected to use a 0-10 scale.

    Default weights intentionally remain visible so that
    the workflow can explain how the score was produced.

    This function does not decide which area should be
    prioritized. It only calculates the numerical result.
    """

    default_weights = {
        "population_impact": 0.20,
        "severity": 0.20,
        "urgency": 0.20,
        "vulnerability": 0.15,
        "resource_shortage": 0.15,
        "accessibility_constraint": 0.10,
    }

    if weights:
        active_weights = default_weights.copy()
        active_weights.update(weights)
    else:
        active_weights = default_weights

    factors = {
        "population_impact": population_impact,
        "severity": severity,
        "urgency": urgency,
        "vulnerability": vulnerability,
        "resource_shortage": resource_shortage,
        "accessibility_constraint": accessibility_constraint,
    }

    normalized_factors = {
        key: min(
            max(float(value), 0.0),
            10.0,
        )
        for key, value in factors.items()
    }

    weighted_values = {
        key: normalized_factors[key]
        * active_weights[key]
        for key in normalized_factors
    }

    score = sum(
        weighted_values.values()
    )

    return {
        "score": round(score, 2),
        "max_score": 10.0,
        "population_impact": normalized_factors[
            "population_impact"
        ],
        "severity": normalized_factors[
            "severity"
        ],
        "urgency": normalized_factors[
            "urgency"
        ],
        "vulnerability": normalized_factors[
            "vulnerability"
        ],
        "resource_shortage": normalized_factors[
            "resource_shortage"
        ],
        "accessibility_constraint": normalized_factors[
            "accessibility_constraint"
        ],
    }


# ============================================================
# RESOURCE ALLOCATION
# ============================================================

def calculate_proportional_allocation(
    total_resource: float,
    demands: Dict[str, float],
) -> Dict[str, float]:
    """
    Calculate proportional allocation across areas based
    on their stated demand.

    The function never allocates more than the available
    total resource.
    """

    total_resource = max(
        float(total_resource),
        0.0,
    )

    cleaned_demands = {
        area: max(float(demand), 0.0)
        for area, demand in demands.items()
    }

    total_demand = sum(
        cleaned_demands.values()
    )

    if total_demand <= 0:
        return {
            area: 0.0
            for area in cleaned_demands
        }

    allocations = {}

    for area, demand in cleaned_demands.items():

        allocation = (
            demand / total_demand
        ) * total_resource

        allocations[area] = round(
            allocation,
            2,
        )

    return allocations


def calculate_fair_share(
    total_resource: float,
    number_of_areas: int,
) -> float:
    """
    Calculate an equal resource share across areas.

    This is a mathematical reference only. The final
    emergency allocation should also consider actual
    needs, urgency, accessibility, and constraints.
    """

    total_resource = max(
        float(total_resource),
        0.0,
    )

    number_of_areas = int(
        number_of_areas
    )

    if number_of_areas <= 0:
        return 0.0

    return round(
        total_resource / number_of_areas,
        2,
    )


# ============================================================
# POPULATION / NEED CALCULATIONS
# ============================================================

def calculate_people_coverage(
    affected_population: int,
    supported_people: int,
) -> Dict[str, float]:
    """
    Calculate the percentage of affected people that can
    currently be supported.
    """

    affected_population = max(
        int(affected_population),
        0,
    )

    supported_people = max(
        int(supported_people),
        0,
    )

    if affected_population == 0:
        return {
            "affected_population": 0,
            "supported_people": 0,
            "coverage_percentage": 100.0,
        }

    coverage = (
        supported_people
        / affected_population
    ) * 100.0

    return {
        "affected_population": affected_population,
        "supported_people": min(
            supported_people,
            affected_population,
        ),
        "coverage_percentage": round(
            min(max(coverage, 0.0), 100.0),
            2,
        ),
    }


# ============================================================
# TOOL REGISTRY
# ============================================================

def get_calculator_tools() -> Dict[str, callable]:
    """
    Return the calculator functions in a simple registry.

    The registry allows the workflow or agent layer to
    selectively expose calculations without coupling the
    application to one implementation.
    """

    return {
        "calculate_shortage": calculate_shortage,
        "calculate_coverage_percentage": (
            calculate_coverage_percentage
        ),
        "calculate_allocation_percentage": (
            calculate_allocation_percentage
        ),
        "calculate_remaining_resource": (
            calculate_remaining_resource
        ),
        "calculate_priority_score": (
            calculate_priority_score
        ),
        "calculate_proportional_allocation": (
            calculate_proportional_allocation
        ),
        "calculate_fair_share": (
            calculate_fair_share
        ),
        "calculate_people_coverage": (
            calculate_people_coverage
        ),
    }
