from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import List, Optional


class Decision(str, Enum):
    REJECT = "REJECT"
    OBSERVE = "OBSERVE"
    INVESTIGATE = "INVESTIGATE"
    VALIDATE = "VALIDATE"
    PILOT = "PILOT"
    COMMIT = "COMMIT"
    SCALE = "SCALE"
    EXIT = "EXIT"


class EvidenceKind(str, Enum):
    VERIFIED = "VERIFIED"
    ESTIMATE = "ESTIMATE"
    ASSUMPTION = "ASSUMPTION"
    UNKNOWN = "UNKNOWN"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    SPECULATIVE = "SPECULATIVE"


@dataclass
class EvidenceItem:
    claim: str
    kind: EvidenceKind
    importance: int = 3
    confidence: int = 3
    source: str = ""
    consequence_if_wrong: str = ""

    def validate(self) -> None:
        if not self.claim.strip():
            raise ValueError("Evidence claim cannot be empty.")
        if not 1 <= self.importance <= 5:
            raise ValueError("importance must be 1..5")
        if not 1 <= self.confidence <= 5:
            raise ValueError("confidence must be 1..5")


@dataclass
class Experiment:
    hypothesis: str
    action: str
    max_cash: float
    max_hours: float
    pass_condition: str
    fail_condition: str

    def validate(self) -> None:
        if not self.hypothesis.strip() or not self.action.strip():
            raise ValueError("Experiment hypothesis and action are required.")
        if self.max_cash < 0 or self.max_hours < 0:
            raise ValueError("Experiment budgets cannot be negative.")


@dataclass
class Project:
    name: str
    objective: str
    beneficiary: str
    value_mechanism: str
    upside_low: float
    upside_base: float
    upside_high: float
    probability_low: float
    probability_base: float
    probability_high: float
    cash_required: float
    hours_required: float
    hourly_value: float = 50.0
    operating_costs: float = 0.0
    downside_cost: float = 0.0
    time_to_signal_days: float = 30.0
    time_to_payoff_days: float = 180.0
    strategic_leverage: int = 3
    reversibility: int = 3
    execution_feasibility: int = 3
    differentiation: int = 3
    reusability: int = 3
    comparative_advantage: int = 3
    opportunity_cost_value: float = 0.0
    competing_project: str = ""
    dependencies: List[str] = field(default_factory=list)
    fatal_constraints: List[str] = field(default_factory=list)
    evidence: List[EvidenceItem] = field(default_factory=list)
    proposed_experiment: Optional[Experiment] = None

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Project name is required.")
        if not self.objective.strip():
            raise ValueError("Project objective is required.")
        if not (0 <= self.probability_low <= self.probability_base <= self.probability_high <= 1):
            raise ValueError("Probabilities must satisfy 0 <= low <= base <= high <= 1.")
        if not (self.upside_low <= self.upside_base <= self.upside_high):
            raise ValueError("Upside must satisfy low <= base <= high.")
        numeric_nonnegative = [
            self.cash_required,
            self.hours_required,
            self.hourly_value,
            self.operating_costs,
            self.downside_cost,
            self.time_to_signal_days,
            self.time_to_payoff_days,
            self.opportunity_cost_value,
        ]
        if any(v < 0 for v in numeric_nonnegative):
            raise ValueError("Cost/time fields cannot be negative.")
        for name in (
            "strategic_leverage",
            "reversibility",
            "execution_feasibility",
            "differentiation",
            "reusability",
            "comparative_advantage",
        ):
            if not 1 <= getattr(self, name) <= 5:
                raise ValueError(f"{name} must be 1..5")
        for item in self.evidence:
            item.validate()
        if self.proposed_experiment:
            self.proposed_experiment.validate()

    def to_dict(self):
        return asdict(self)
