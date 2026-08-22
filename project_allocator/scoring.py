from __future__ import annotations

from .economics import base_roi
from .evidence import evidence_quality
from .models import Project


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _scale_1_to_5(value: int, max_points: float) -> float:
    return ((value - 1) / 4.0) * max_points


def summary_score(project: Project) -> int:
    """Return a diagnostic 0..100 score. It never overrides decision gates."""
    roi = base_roi(project)
    economic = 20.0 if roi == float("inf") else _clamp((roi + 0.5) / 3.0, 0.0, 1.0) * 20.0
    evidence = evidence_quality(project) * 15.0
    speed = _clamp(1.0 - project.time_to_signal_days / 180.0, 0.0, 1.0) * 15.0
    strategic = _scale_1_to_5(project.strategic_leverage, 15.0)
    feasibility = _scale_1_to_5(project.execution_feasibility, 10.0)
    downside = _scale_1_to_5(project.reversibility, 10.0)
    differentiation = _scale_1_to_5(project.differentiation, 5.0)
    reusability = _scale_1_to_5(project.reusability, 5.0)
    advantage = _scale_1_to_5(project.comparative_advantage, 5.0)

    return round(
        economic
        + evidence
        + speed
        + strategic
        + feasibility
        + downside
        + differentiation
        + reusability
        + advantage
    )
