from __future__ import annotations

import json
from pathlib import Path

from .models import EvidenceItem, EvidenceKind, Experiment, Project


def project_from_dict(data: dict) -> Project:
    evidence = [
        EvidenceItem(
            claim=item["claim"],
            kind=EvidenceKind(item["kind"]),
            importance=int(item.get("importance", 3)),
            confidence=int(item.get("confidence", 3)),
            source=item.get("source", ""),
            consequence_if_wrong=item.get("consequence_if_wrong", ""),
        )
        for item in data.get("evidence", [])
    ]

    experiment_data = data.get("proposed_experiment")
    experiment = None
    if experiment_data:
        experiment = Experiment(
            hypothesis=experiment_data["hypothesis"],
            action=experiment_data["action"],
            max_cash=float(experiment_data["max_cash"]),
            max_hours=float(experiment_data["max_hours"]),
            pass_condition=experiment_data["pass_condition"],
            fail_condition=experiment_data["fail_condition"],
        )

    normalized = dict(data)
    normalized["evidence"] = evidence
    normalized["proposed_experiment"] = experiment
    return Project(**normalized)


def load_project(path: str | Path) -> Project:
    with open(path, "r", encoding="utf-8") as handle:
        return project_from_dict(json.load(handle))


def dump_project(project: Project, path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(project.to_dict(), handle, indent=2, default=str)
