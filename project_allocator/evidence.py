from __future__ import annotations

from .models import Confidence, EvidenceKind, Project


_KIND_WEIGHT = {
    EvidenceKind.VERIFIED: 1.00,
    EvidenceKind.ESTIMATE: 0.65,
    EvidenceKind.ASSUMPTION: 0.30,
    EvidenceKind.UNKNOWN: 0.05,
}


def evidence_quality(project: Project) -> float:
    """Return 0..1 evidence quality, importance-weighted."""
    if not project.evidence:
        return 0.0

    weighted = 0.0
    total_importance = 0.0
    for item in project.evidence:
        importance = float(item.importance)
        confidence_factor = item.confidence / 5.0
        weighted += importance * _KIND_WEIGHT[item.kind] * confidence_factor
        total_importance += importance

    return 0.0 if total_importance == 0 else weighted / total_importance


def evidence_confidence(project: Project) -> Confidence:
    q = evidence_quality(project)
    if q >= 0.78:
        return Confidence.HIGH
    if q >= 0.55:
        return Confidence.MEDIUM
    if q >= 0.30:
        return Confidence.LOW
    return Confidence.SPECULATIVE


def critical_unknowns(project: Project):
    weak = []
    for item in project.evidence:
        if item.kind in (EvidenceKind.ASSUMPTION, EvidenceKind.UNKNOWN) or item.confidence <= 2:
            weak.append(item)
    return sorted(weak, key=lambda x: (x.importance, -x.confidence), reverse=True)
