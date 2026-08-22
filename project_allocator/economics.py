from __future__ import annotations

from dataclasses import dataclass

from .models import Project


@dataclass(frozen=True)
class EconomicScenario:
    name: str
    upside: float
    probability: float
    expected_gross_value: float
    total_resource_cost: float
    net_expected_value: float


def total_resource_cost(project: Project) -> float:
    return (
        project.cash_required
        + project.operating_costs
        + project.downside_cost
        + (project.hours_required * project.hourly_value)
        + project.opportunity_cost_value
    )


def scenario(project: Project, name: str) -> EconomicScenario:
    key = name.lower()
    if key == "low":
        upside, probability = project.upside_low, project.probability_low
    elif key == "base":
        upside, probability = project.upside_base, project.probability_base
    elif key == "high":
        upside, probability = project.upside_high, project.probability_high
    else:
        raise ValueError("Scenario must be low, base, or high.")

    gross = upside * probability
    costs = total_resource_cost(project)
    return EconomicScenario(
        name=key,
        upside=upside,
        probability=probability,
        expected_gross_value=gross,
        total_resource_cost=costs,
        net_expected_value=gross - costs,
    )


def all_scenarios(project: Project):
    return [scenario(project, "low"), scenario(project, "base"), scenario(project, "high")]


def base_roi(project: Project) -> float:
    current = scenario(project, "base")
    if current.total_resource_cost <= 0:
        return float("inf") if current.net_expected_value > 0 else 0.0
    return current.net_expected_value / current.total_resource_cost
