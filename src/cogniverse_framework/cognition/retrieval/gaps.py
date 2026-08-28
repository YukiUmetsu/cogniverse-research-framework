"""Cognitive gap and information-need contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar

from .._validation import normalize_identifiers, validate_identifier, validate_ppm


class GapKind(str, Enum):
    """Typed missing-information categories that can drive retrieval."""

    UNKNOWN_CAUSE = "unknown_cause"
    UNKNOWN_DESTINATION = "unknown_destination"
    UNKNOWN_GOAL_PRECONDITION = "unknown_goal_precondition"
    LOW_PREDICTION_CONFIDENCE = "low_prediction_confidence"
    UNRESOLVED_BELIEF_CONFLICT = "unresolved_belief_conflict"
    MISSING_ASSOCIATION = "missing_association"


@dataclass(frozen=True, slots=True)
class CognitiveGap:
    """Explicit representation of missing information in the active workspace."""

    SCHEMA_VERSION: ClassVar[str] = "cognitive_gap.v1"

    gap_id: str
    kind: GapKind
    subject_node_id: str
    source_system: str
    logical_step: int
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    urgency_ppm: int | None = None

    def __post_init__(self) -> None:
        validate_identifier("gap_id", self.gap_id)
        validate_identifier("subject_node_id", self.subject_node_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        validate_ppm("urgency_ppm", self.urgency_ppm)
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "gap_id": self.gap_id,
            "kind": self.kind.value,
            "subject_node_id": self.subject_node_id,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "evidence_ids": list(self.evidence_ids),
            "urgency_ppm": self.urgency_ppm,
        }


@dataclass(frozen=True, slots=True)
class InformationNeed:
    """Motivational view of a gap: what information is required and how urgently."""

    SCHEMA_VERSION: ClassVar[str] = "information_need.v1"

    need_id: str
    gap_id: str
    kind: GapKind
    subject_node_id: str
    logical_step: int
    priority_ppm: int
    source_system: str

    def __post_init__(self) -> None:
        validate_identifier("need_id", self.need_id)
        validate_identifier("gap_id", self.gap_id)
        validate_identifier("subject_node_id", self.subject_node_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        validate_ppm("priority_ppm", self.priority_ppm)

    @classmethod
    def from_gap(
        cls,
        gap: CognitiveGap,
        *,
        need_id: str | None = None,
        default_priority_ppm: int = 500_000,
    ) -> InformationNeed:
        return cls(
            need_id=need_id or f"need.{gap.gap_id}",
            gap_id=gap.gap_id,
            kind=gap.kind,
            subject_node_id=gap.subject_node_id,
            logical_step=gap.logical_step,
            priority_ppm=gap.urgency_ppm
            if gap.urgency_ppm is not None
            else default_priority_ppm,
            source_system=gap.source_system,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "need_id": self.need_id,
            "gap_id": self.gap_id,
            "kind": self.kind.value,
            "subject_node_id": self.subject_node_id,
            "logical_step": self.logical_step,
            "priority_ppm": self.priority_ppm,
            "source_system": self.source_system,
        }
