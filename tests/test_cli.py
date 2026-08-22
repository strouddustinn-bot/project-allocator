import tempfile
import unittest
from pathlib import Path

from project_allocator.cli import _evaluate_and_persist
from project_allocator.db import connect, list_latest
from project_allocator.intake import save_interactive_project
from project_allocator.models import EvidenceItem, EvidenceKind, Experiment, Project


def sample_project():
    return Project(
        name="First Gate Test",
        objective="Validate the first usable workflow",
        beneficiary="Operator",
        value_mechanism="Avoid wasting resources on weak projects",
        upside_low=1000,
        upside_base=10000,
        upside_high=30000,
        probability_low=0.2,
        probability_base=0.5,
        probability_high=0.8,
        cash_required=500,
        hours_required=10,
        hourly_value=50,
        time_to_signal_days=7,
        strategic_leverage=5,
        reversibility=5,
        execution_feasibility=5,
        differentiation=3,
        reusability=5,
        comparative_advantage=4,
        evidence=[
            EvidenceItem(
                claim="The operator has multiple competing projects",
                kind=EvidenceKind.VERIFIED,
                importance=5,
                confidence=5,
                source="Observed project portfolio",
            ),
            EvidenceItem(
                claim="The allocator will materially improve choices",
                kind=EvidenceKind.ASSUMPTION,
                importance=5,
                confidence=2,
            ),
        ],
        proposed_experiment=Experiment(
            hypothesis="The engine changes at least one real resource-allocation decision",
            action="Run three real projects through the engine and compare the ranking to prior intent",
            max_cash=0,
            max_hours=2,
            pass_condition="At least one decision changes for a defensible reason",
            fail_condition="The engine adds no useful discrimination",
        ),
    )


class CliWorkflowTests(unittest.TestCase):
    def test_first_user_gate_persists_project_and_evaluation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / ".pursuit" / "allocator.db"
            project_dir = root / ".pursuit" / "projects"
            project = sample_project()

            snapshot = save_interactive_project(project, project_dir)
            result = _evaluate_and_persist(project, str(db))

            self.assertTrue(snapshot.exists())
            self.assertTrue(db.exists())
            self.assertGreaterEqual(result.score, 0)

            conn = connect(db)
            rows = list_latest(conn)
            conn.close()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["project_name"], project.name)


if __name__ == "__main__":
    unittest.main()
