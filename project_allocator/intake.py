from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from .models import EvidenceItem, EvidenceKind, Experiment, Project
from .serde import dump_project


InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]


def _prompt_text(label: str, *, default: str | None = None, required: bool = True, input_fn: InputFn = input) -> str:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input_fn(f"{label}{suffix}: ").strip()
        if raw:
            return raw
        if default is not None:
            return default
        if not required:
            return ""
        print("  Required. Please enter a value.")


def _prompt_float(label: str, *, default: float = 0.0, minimum: float = 0.0, input_fn: InputFn = input) -> float:
    while True:
        raw = input_fn(f"{label} [{default:g}]: ").strip()
        if not raw:
            return float(default)
        try:
            value = float(raw.replace(",", ""))
        except ValueError:
            print("  Enter a number.")
            continue
        if value < minimum:
            print(f"  Must be at least {minimum:g}.")
            continue
        return value


def _prompt_int_range(label: str, *, default: int = 3, low: int = 1, high: int = 5, input_fn: InputFn = input) -> int:
    while True:
        raw = input_fn(f"{label} [{default}] ({low}-{high}): ").strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError:
            print("  Enter a whole number.")
            continue
        if not low <= value <= high:
            print(f"  Must be between {low} and {high}.")
            continue
        return value


def _prompt_probability(label: str, *, default: float, input_fn: InputFn = input) -> float:
    while True:
        raw = input_fn(f"{label} [{default * 100:g}%]: ").strip()
        if not raw:
            return default
        raw = raw.rstrip("%").strip()
        try:
            value = float(raw)
        except ValueError:
            print("  Enter a probability such as 40%, 40, or 0.40.")
            continue
        if value > 1:
            value /= 100.0
        if not 0 <= value <= 1:
            print("  Probability must be between 0% and 100%.")
            continue
        return value


def _prompt_yes_no(label: str, *, default: bool = False, input_fn: InputFn = input) -> bool:
    marker = "Y/n" if default else "y/N"
    while True:
        raw = input_fn(f"{label} [{marker}]: ").strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("  Enter y or n.")


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "project"


def _collect_evidence(input_fn: InputFn = input) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []
    while True:
        claim = _prompt_text("Critical claim / evidence item (blank to stop)", required=False, input_fn=input_fn)
        if not claim:
            break
        while True:
            raw_kind = _prompt_text(
                "Type: VERIFIED / ESTIMATE / ASSUMPTION / UNKNOWN",
                default="ASSUMPTION",
                input_fn=input_fn,
            ).upper()
            try:
                kind = EvidenceKind(raw_kind)
                break
            except ValueError:
                print("  Use VERIFIED, ESTIMATE, ASSUMPTION, or UNKNOWN.")
        evidence.append(
            EvidenceItem(
                claim=claim,
                kind=kind,
                importance=_prompt_int_range("Importance if this claim is wrong", default=5, input_fn=input_fn),
                confidence=_prompt_int_range(
                    "Confidence in this claim",
                    default=2 if kind in {EvidenceKind.ASSUMPTION, EvidenceKind.UNKNOWN} else 4,
                    input_fn=input_fn,
                ),
                source=_prompt_text("Source / basis", required=False, input_fn=input_fn),
                consequence_if_wrong=_prompt_text("What happens if it is wrong", required=False, input_fn=input_fn),
            )
        )
        if not _prompt_yes_no("Add another evidence item?", default=False, input_fn=input_fn):
            break
    return evidence


def _collect_experiment(input_fn: InputFn = input) -> Experiment | None:
    if not _prompt_yes_no("Define a bounded validation experiment now?", default=True, input_fn=input_fn):
        return None
    return Experiment(
        hypothesis=_prompt_text("Hypothesis to test", input_fn=input_fn),
        action=_prompt_text("Exact validation action", input_fn=input_fn),
        max_cash=_prompt_float("Maximum cash authorized for this test ($)", default=100, input_fn=input_fn),
        max_hours=_prompt_float("Maximum hours authorized for this test", default=6, input_fn=input_fn),
        pass_condition=_prompt_text("PASS condition", input_fn=input_fn),
        fail_condition=_prompt_text("FAIL condition", input_fn=input_fn),
    )


def interactive_project(input_fn: InputFn = input, output_fn: OutputFn = print) -> Project:
    output_fn("\nPROJECT ALLOCATOR — USER GATE 1: PROJECT INTAKE")
    output_fn("Answer with conservative estimates. Unknowns are allowed; fake certainty is not.\n")

    name = _prompt_text("Project name", input_fn=input_fn)
    objective = _prompt_text("What outcome are you trying to create?", input_fn=input_fn)
    beneficiary = _prompt_text("Who specifically benefits / pays / uses it?", input_fn=input_fn)
    value_mechanism = _prompt_text("How does it create measurable value?", input_fn=input_fn)

    output_fn("\nEconomics — use realistic outcome values, not fantasy ceilings.")
    upside_low = _prompt_float("Low-case payoff / value ($)", default=0, input_fn=input_fn)
    upside_base = _prompt_float("Base-case payoff / value ($)", default=max(upside_low, 1000), input_fn=input_fn)
    upside_high = _prompt_float("High-case payoff / value ($)", default=max(upside_base, 5000), input_fn=input_fn)
    upside_base = max(upside_base, upside_low)
    upside_high = max(upside_high, upside_base)

    output_fn("\nProbability — enter 40%, 40, or 0.40.")
    probabilities = sorted([
        _prompt_probability("Low-case probability", default=0.20, input_fn=input_fn),
        _prompt_probability("Base-case probability", default=0.45, input_fn=input_fn),
        _prompt_probability("High-case probability", default=0.70, input_fn=input_fn),
    ])

    output_fn("\nResource burden.")
    cash_required = _prompt_float("Cash required for full current plan ($)", default=0, input_fn=input_fn)
    hours_required = _prompt_float("Hours required for full current plan", default=10, input_fn=input_fn)
    hourly_value = _prompt_float("Value of one hour of your time ($)", default=50, input_fn=input_fn)
    operating_costs = _prompt_float("Other operating costs ($)", default=0, input_fn=input_fn)
    downside_cost = _prompt_float("Additional downside if it fails ($)", default=0, input_fn=input_fn)
    opportunity_cost_value = _prompt_float("Value of best displaced alternative ($)", default=0, input_fn=input_fn)
    competing_project = _prompt_text("Best competing project / use of resources", required=False, input_fn=input_fn)

    output_fn("\nTiming.")
    time_to_signal_days = _prompt_float("Days until useful evidence arrives", default=14, input_fn=input_fn)
    time_to_payoff_days = _prompt_float("Days until meaningful payoff", default=90, input_fn=input_fn)

    output_fn("\nRate 1 (weak) to 5 (strong).")
    strategic_leverage = _prompt_int_range("Strategic leverage", default=3, input_fn=input_fn)
    reversibility = _prompt_int_range("Reversibility", default=4, input_fn=input_fn)
    execution_feasibility = _prompt_int_range("Execution feasibility", default=3, input_fn=input_fn)
    differentiation = _prompt_int_range("Differentiation", default=3, input_fn=input_fn)
    reusability = _prompt_int_range("Reusable assets created", default=3, input_fn=input_fn)
    comparative_advantage = _prompt_int_range("Your comparative advantage", default=3, input_fn=input_fn)

    output_fn("\nEvidence ledger. Start with the claim most capable of killing the project.")
    evidence = _collect_evidence(input_fn=input_fn)

    fatal_constraints: list[str] = []
    if _prompt_yes_no("Any known hard blocker or fatal constraint?", default=False, input_fn=input_fn):
        while True:
            fatal_constraints.append(_prompt_text("Blocker", input_fn=input_fn))
            if not _prompt_yes_no("Add another blocker?", default=False, input_fn=input_fn):
                break

    project = Project(
        name=name,
        objective=objective,
        beneficiary=beneficiary,
        value_mechanism=value_mechanism,
        upside_low=upside_low,
        upside_base=upside_base,
        upside_high=upside_high,
        probability_low=probabilities[0],
        probability_base=probabilities[1],
        probability_high=probabilities[2],
        cash_required=cash_required,
        hours_required=hours_required,
        hourly_value=hourly_value,
        operating_costs=operating_costs,
        downside_cost=downside_cost,
        time_to_signal_days=time_to_signal_days,
        time_to_payoff_days=time_to_payoff_days,
        strategic_leverage=strategic_leverage,
        reversibility=reversibility,
        execution_feasibility=execution_feasibility,
        differentiation=differentiation,
        reusability=reusability,
        comparative_advantage=comparative_advantage,
        opportunity_cost_value=opportunity_cost_value,
        competing_project=competing_project,
        fatal_constraints=fatal_constraints,
        evidence=evidence,
        proposed_experiment=_collect_experiment(input_fn=input_fn),
    )
    project.validate()
    return project


def save_interactive_project(project: Project, directory: str | Path) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{_slugify(project.name)}.json"
    dump_project(project, path)
    return path
