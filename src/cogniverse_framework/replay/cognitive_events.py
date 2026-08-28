"""Replay helpers for typed cognitive runtime event streams."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, ClassVar, Iterable

from cogniverse_framework.cognition.backends.events import CognitiveEvent


@dataclass(frozen=True, slots=True)
class CognitiveEventTrace:
    """Deterministic, auditable sequence of cognitive runtime events."""

    SCHEMA_VERSION: ClassVar[str] = "cognitive_event_trace.v1"

    source_system: str
    events: tuple[CognitiveEvent, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        normalized = tuple(sorted(self.events, key=lambda item: (item.logical_step, item.event_id)))
        object.__setattr__(self, "events", normalized)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "source_system": self.source_system,
            "events": [event.to_dict() for event in self.events],
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
    def from_dict(cls, payload: dict[str, Any]) -> CognitiveEventTrace:
        return cls(
            source_system=payload["source_system"],
            events=tuple(
                CognitiveEvent.from_dict(item) for item in payload.get("events", ())
            ),
        )


def build_event_trace(
    events: Iterable[CognitiveEvent],
    *,
    source_system: str,
) -> CognitiveEventTrace:
    return CognitiveEventTrace(source_system=source_system, events=tuple(events))


def event_trace_to_evidence_payload(trace: CognitiveEventTrace) -> dict[str, Any]:
    """Serialize a cognitive event trace for evidence storage."""

    return {
        "artifact_kind": "cognitive_event_trace",
        "trace_digest": trace.digest(),
        "trace": trace.to_dict(),
    }


def compare_event_traces(
    left: CognitiveEventTrace,
    right: CognitiveEventTrace,
) -> dict[str, Any]:
    """Compare two event traces and report the first divergence."""

    left_digests = tuple(event.digest() for event in left.events)
    right_digests = tuple(event.digest() for event in right.events)
    shared = min(len(left_digests), len(right_digests))
    first_index = next(
        (index for index in range(shared) if left_digests[index] != right_digests[index]),
        None,
    )
    if first_index is not None:
        return {
            "equal": False,
            "first_divergence_index": first_index,
            "left_event_id": left.events[first_index].event_id,
            "right_event_id": right.events[first_index].event_id,
        }
    if len(left_digests) != len(right_digests):
        return {
            "equal": False,
            "first_divergence_index": shared,
            "left_length": len(left_digests),
            "right_length": len(right_digests),
        }
    return {"equal": True, "trace_digest": left.digest()}


def replay_event_trace(trace: CognitiveEventTrace) -> tuple[CognitiveEvent, ...]:
    """Return the canonical event order for audit replay."""

    return trace.events
