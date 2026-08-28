"""Typed cognitive runtime events for pluggable event buses."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, ClassVar

from .._validation import normalize_identifiers, validate_identifier


class CognitiveEventKind(str, Enum):
    """Versioned event kinds for the cognitive runtime."""

    PERCEPT_RECEIVED = "percept_received"
    NODE_ACTIVATED = "node_activated"
    NODE_EVICTED = "node_evicted"
    MEMORY_PRIMED = "memory_primed"
    MEMORY_RETRIEVED = "memory_retrieved"
    COGNITIVE_GAP_CREATED = "cognitive_gap_created"
    COGNITIVE_GAP_RESOLVED = "cognitive_gap_resolved"
    PREDICTION_CREATED = "prediction_created"
    PREDICTION_ERROR_OBSERVED = "prediction_error_observed"
    GOAL_CHANGED = "goal_changed"
    ACTION_PROPOSED = "action_proposed"
    ACTION_SELECTED = "action_selected"


@dataclass(frozen=True, slots=True)
class CognitiveEvent:
    """Immutable, replayable cognitive runtime event."""

    SCHEMA_VERSION: ClassVar[str] = "cognitive_event.v1"

    event_id: str
    kind: CognitiveEventKind
    logical_step: int
    source_system: str
    subject_id: str
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    payload_sha256: str | None = None

    def __post_init__(self) -> None:
        validate_identifier("event_id", self.event_id)
        validate_identifier("source_system", self.source_system)
        validate_identifier("subject_id", self.subject_id)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "event_id": self.event_id,
            "kind": self.kind.value,
            "logical_step": self.logical_step,
            "source_system": self.source_system,
            "subject_id": self.subject_id,
            "evidence_ids": list(self.evidence_ids),
            "payload_sha256": self.payload_sha256,
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> CognitiveEvent:
        kind = payload["kind"]
        if not isinstance(kind, CognitiveEventKind):
            kind = CognitiveEventKind(kind)
        return cls(
            event_id=payload["event_id"],
            kind=kind,
            logical_step=payload["logical_step"],
            source_system=payload["source_system"],
            subject_id=payload["subject_id"],
            evidence_ids=tuple(payload.get("evidence_ids", ())),
            payload_sha256=payload.get("payload_sha256"),
        )
