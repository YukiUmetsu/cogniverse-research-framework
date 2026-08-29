"""Deterministic hard-constraint evaluation (F2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Iterable

from ._validation import normalize_identifiers, validate_identifier
from .value import ConstraintViolation, HardConstraint


@dataclass(frozen=True, slots=True)
class ConstraintEvaluation:
    """Outcome of evaluating one candidate subject against hard constraints."""

    SCHEMA_VERSION: ClassVar[str] = "constraint_evaluation.v1"

    subject_id: str
    logical_step: int
    source_system: str
    allowed: bool
    violations: tuple[ConstraintViolation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("subject_id", self.subject_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        object.__setattr__(
            self,
            "violations",
            tuple(sorted(self.violations, key=lambda item: item.violation_id)),
        )
        if self.allowed and self.violations:
            raise ValueError("allowed evaluations must not contain violations")
        if not self.allowed and not self.violations:
            raise ValueError("blocked evaluations must contain at least one violation")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "subject_id": self.subject_id,
            "logical_step": self.logical_step,
            "source_system": self.source_system,
            "allowed": self.allowed,
            "violations": [violation.to_dict() for violation in self.violations],
        }


def evaluate_hard_constraints(
    constraints: Iterable[HardConstraint],
    *,
    subject_id: str,
    logical_step: int,
    source_system: str,
    evidence_ids: tuple[str, ...] = (),
) -> ConstraintEvaluation:
    """Evaluate whether a subject is allowed under injected hard constraints.

    A constraint blocks when ``subject_id`` appears in its ``blocked_subject_ids``.
    Hard constraints are non-compensatable: any block rejects the subject regardless
    of soft value.
    """

    validate_identifier("subject_id", subject_id)
    validate_identifier("source_system", source_system)
    normalized_evidence = normalize_identifiers("evidence_ids", tuple(evidence_ids))
    violations: list[ConstraintViolation] = []
    violation_counter = 0

    for constraint in sorted(constraints, key=lambda item: item.constraint_id):
        if logical_step < constraint.logical_step:
            continue
        if subject_id not in constraint.blocked_subject_ids:
            continue
        violation_counter += 1
        combined_evidence = normalized_evidence + constraint.evidence_ids
        violations.append(
            ConstraintViolation(
                violation_id=f"violation-{violation_counter:06d}",
                constraint_id=constraint.constraint_id,
                source_system=source_system,
                logical_step=logical_step,
                subject_id=subject_id,
                evidence_ids=normalize_identifiers(
                    "evidence_ids",
                    tuple(dict.fromkeys(combined_evidence)),
                ),
            )
        )

    if violations:
        return ConstraintEvaluation(
            subject_id=subject_id,
            logical_step=logical_step,
            source_system=source_system,
            allowed=False,
            violations=tuple(violations),
        )
    return ConstraintEvaluation(
        subject_id=subject_id,
        logical_step=logical_step,
        source_system=source_system,
        allowed=True,
    )
