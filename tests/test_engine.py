import unittest

from project_allocator.decision import evaluate
from project_allocator.models import Confidence, Decision, EvidenceItem, EvidenceKind, Experiment, Project


def base_project(**overrides):
    project = Project(
        name="Test",
        objective="Test objective",
        beneficiary="Customer",
        value_mechanism="Creates measurable value",
        upside_low=1000,
        upside_base=10000,
        upside_high=30000,
        probability_low=0.2,
        probability_base=0.5,
        probability_high=0.8,
        cash_required=500,
        hours_required=10,
        hourly_value=50,
        operating_costs=0,
        downside_cost=0,
        time_to_signal_days=14,
        strategic_leverage=4,
        reversibility=4,
        execution_feasibility=4,
        differentiation=3,
        reusability=4,
        comparative_advantage=4,
        evidence=[],
    )
    for key, value in overrides.items():
        setattr(project, key, value)
    return project


class DecisionTests(unittest.TestCase):
    def test_fatal_constraint_rejects(self):
        project = base_project(fatal_constraints=["Requires unavailable license"])
        result = evaluate(project)
        self.assertEqual(result.decision, Decision.REJECT)
        self.assertEqual(result.authorized_cash, 0)

    def test_low_evidence_validates_when_experiment_exists(self):
        project = base_project(
            evidence=[EvidenceItem(claim="Customers will pay", kind=EvidenceKind.ASSUMPTION, importance=5, confidence=2)],
            proposed_experiment=Experiment(
                hypothesis="3 customers will commit",
                action="Ask 20 customers for a paid commitment",
                max_cash=100,
                max_hours=6,
                pass_condition=">=3 commitments",
                fail_condition="<=1 commitment",
            ),
        )
        result = evaluate(project)
        self.assertEqual(result.decision, Decision.VALIDATE)
        self.assertEqual(result.authorized_cash, 100)
        self.assertEqual(result.authorized_hours, 6)

    def test_high_evidence_positive_economics_can_commit(self):
        evidence = [
            EvidenceItem(claim=f"Verified claim {index}", kind=EvidenceKind.VERIFIED, importance=5, confidence=5)
            for index in range(3)
        ]
        result = evaluate(base_project(evidence=evidence))
        self.assertEqual(result.confidence, Confidence.HIGH)
        self.assertEqual(result.decision, Decision.COMMIT)

    def test_high_scenario_negative_rejects(self):
        project = base_project(
            upside_low=100,
            upside_base=200,
            upside_high=300,
            probability_low=0.1,
            probability_base=0.2,
            probability_high=0.3,
            cash_required=5000,
            hours_required=100,
            evidence=[EvidenceItem(claim="Verified demand", kind=EvidenceKind.VERIFIED, importance=5, confidence=5)],
        )
        self.assertEqual(evaluate(project).decision, Decision.REJECT)


if __name__ == "__main__":
    unittest.main()
