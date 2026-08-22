from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .economics import all_scenarios, base_roi
from .evidence import critical_unknowns, evidence_confidence
from .models import Confidence, Decision, Project
from .scoring import summary_score


@dataclass
class Evaluation:
    decision: Decision
    score: int
    confidence: Confidence
    reasons: List[str]
    blockers: List[str]
    next_action: str
    authorized_cash: float
    authorized_hours: float


def evaluate(project: Project) -> Evaluation:
    project.validate()
    score = summary_score(project)
    confidence = evidence_confidence(project)
    reasons: List[str] = []
    blockers: List[str] = []

    if not project.beneficiary.strip():
        blockers.append("No identifiable beneficiary/customer/user.")
    if not project.value_mechanism.strip():
        blockers.append("No credible value-creation mechanism defined.")
    blockers.extend(project.fatal_constraints)

    low, base, high = all_scenarios(project)
    roi = base_roi(project)
    unknowns = critical_unknowns(project)

    if blockers:
        return Evaluation(
            Decision.REJECT,
            score,
            confidence,
            reasons,
            blockers,
            "Resolve the fatal constraint before allocating meaningful resources.",
            0.0,
            0.0,
        )

    if base.net_expected_value < 0 and high.net_expected_value <= 0:
        reasons.append("Even the high scenario does not clear total resource cost.")
        return Evaluation(
            Decision.REJECT,
            score,
            confidence,
            reasons,
            blockers,
            "Do not allocate further resources unless the economics materially change.",
            0.0,
            0.0,
        )

    if confidence in (Confidence.SPECULATIVE, Confidence.LOW):
        if project.proposed_experiment:
            experiment = project.proposed_experiment
            reasons.append("Potential exists, but evidence is too weak for meaningful commitment.")
            if unknowns:
                reasons.append(f"Critical weak claim: {unknowns[0].claim}")
            return Evaluation(
                Decision.VALIDATE,
                score,
                confidence,
                reasons,
                blockers,
                experiment.action,
                experiment.max_cash,
                experiment.max_hours,
            )
        reasons.append("Evidence is too weak for meaningful commitment.")
        return Evaluation(
            Decision.INVESTIGATE,
            score,
            confidence,
            reasons,
            blockers,
            "Define the cheapest falsifiable test for the highest-impact assumption.",
            min(project.cash_required, 100.0),
            min(project.hours_required, 4.0),
        )

    if confidence == Confidence.MEDIUM:
        if base.net_expected_value > 0 and roi > 0:
            reasons.append("Base economics are positive, but evidence is not yet strong enough for full commitment.")
            if project.proposed_experiment:
                experiment = project.proposed_experiment
                return Evaluation(
                    Decision.PILOT,
                    score,
                    confidence,
                    reasons,
                    blockers,
                    experiment.action,
                    experiment.max_cash,
                    experiment.max_hours,
                )
            return Evaluation(
                Decision.PILOT,
                score,
                confidence,
                reasons,
                blockers,
                "Run a bounded real-world pilot and record actual costs, time, and outcome.",
                min(project.cash_required, 500.0),
                min(project.hours_required, 20.0),
            )
        return Evaluation(
            Decision.OBSERVE,
            score,
            confidence,
            ["Evidence is moderate but base economics are not compelling."],
            blockers,
            "Wait for better economics or stronger evidence before allocating resources.",
            0.0,
            0.0,
        )

    if confidence == Confidence.HIGH:
        if base.net_expected_value > 0 and roi >= 0.25:
            if project.time_to_signal_days <= 90 and project.execution_feasibility >= 3:
                reasons.append("Evidence is strong and base economics clear the commitment threshold.")
                return Evaluation(
                    Decision.COMMIT,
                    score,
                    confidence,
                    reasons,
                    blockers,
                    "Allocate the planned project resources, with milestone reviews.",
                    project.cash_required,
                    project.hours_required,
                )
            reasons.append("Economics are attractive, but execution/signal timing argues for a smaller pilot.")
            return Evaluation(
                Decision.PILOT,
                score,
                confidence,
                reasons,
                blockers,
                "Run a bounded pilot before full allocation.",
                min(project.cash_required, 500.0),
                min(project.hours_required, 20.0),
            )

        reasons.append("Evidence is strong, but economics do not justify commitment.")
        return Evaluation(
            Decision.OBSERVE,
            score,
            confidence,
            reasons,
            blockers,
            "Do not commit until expected economics improve.",
            0.0,
            0.0,
        )

    return Evaluation(
        Decision.OBSERVE,
        score,
        confidence,
        reasons,
        blockers,
        "Reassess when material new evidence appears.",
        0.0,
        0.0,
    )
