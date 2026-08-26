"""Minimal immutable cognitive-state coordination contract.

This module carries references between cognitive subsystems. It deliberately
does not implement a controller, world model, memory store, value policy, or
task adapter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, ClassVar

from ._validation import normalize_identifiers, validate_identifier, validate_ppm


class ReferenceKind(str, Enum):
    """The cognitive role owned by a reference."""

    GOAL = "goal"
    NEED = "need"
    BELIEF = "belief"
    PREDICTION = "prediction"
    MEMORY = "memory"
    ACTION = "action"


class MemoryKind(str, Enum):
    """The distinct long-term-memory role of a referenced record."""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


@dataclass(frozen=True, slots=True)
class CognitiveReference:
    """A provenance-bearing pointer to subsystem-owned cognitive content."""

    SCHEMA_VERSION: ClassVar[str] = "cognitive_reference.v1"

    ref_id: str
    kind: ReferenceKind
    source_system: str
    logical_step: int
    confidence_ppm: int | None = None
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    memory_kind: MemoryKind | None = None

    def __post_init__(self) -> None:
        validate_identifier("ref_id", self.ref_id)
        validate_identifier("source_system", self.source_system)
        if isinstance(self.logical_step, bool) or not isinstance(self.logical_step, int) or self.logical_step < 0:
            raise ValueError("logical_step must be a non-negative integer")
        validate_ppm("confidence_ppm", self.confidence_ppm)
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )
        if self.kind is ReferenceKind.MEMORY and self.memory_kind is None:
            raise ValueError("memory_kind is required for memory references")
        if self.kind is not ReferenceKind.MEMORY and self.memory_kind is not None:
            raise ValueError("memory_kind is only valid for memory references")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "ref_id": self.ref_id,
            "kind": self.kind.value,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "confidence_ppm": self.confidence_ppm,
            "evidence_ids": list(self.evidence_ids),
            "memory_kind": self.memory_kind.value if self.memory_kind else None,
        }


@dataclass(frozen=True, slots=True)
class CognitiveState:
    """A small typed snapshot for cross-subsystem coordination."""

    SCHEMA_VERSION: ClassVar[str] = "cognitive_state.v1"

    state_id: str
    logical_step: int
    goals: tuple[CognitiveReference, ...] = field(default_factory=tuple)
    needs: tuple[CognitiveReference, ...] = field(default_factory=tuple)
    beliefs: tuple[CognitiveReference, ...] = field(default_factory=tuple)
    predictions: tuple[CognitiveReference, ...] = field(default_factory=tuple)
    memories: tuple[CognitiveReference, ...] = field(default_factory=tuple)
    possible_actions: tuple[CognitiveReference, ...] = field(default_factory=tuple)
    uncertainty_ppm: int | None = None
    hard_constraint_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("state_id", self.state_id)
        if isinstance(self.logical_step, bool) or not isinstance(self.logical_step, int) or self.logical_step < 0:
            raise ValueError("logical_step must be a non-negative integer")
        validate_ppm("uncertainty_ppm", self.uncertainty_ppm)

        collections = (
            ("goals", ReferenceKind.GOAL),
            ("needs", ReferenceKind.NEED),
            ("beliefs", ReferenceKind.BELIEF),
            ("predictions", ReferenceKind.PREDICTION),
            ("memories", ReferenceKind.MEMORY),
            ("possible_actions", ReferenceKind.ACTION),
        )
        all_ids: list[str] = []
        for name, expected_kind in collections:
            items = tuple(getattr(self, name))
            if any(item.kind is not expected_kind for item in items):
                raise ValueError(
                    f"{name} must contain only {expected_kind.value} references"
                )
            normalized = tuple(sorted(items, key=lambda item: item.ref_id))
            object.__setattr__(self, name, normalized)
            all_ids.extend(item.ref_id for item in normalized)

        if len(all_ids) != len(set(all_ids)):
            raise ValueError("reference IDs must be unique across CognitiveState")
        object.__setattr__(
            self,
            "hard_constraint_ids",
            normalize_identifiers(
                "hard_constraint_ids", tuple(self.hard_constraint_ids)
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "state_id": self.state_id,
            "logical_step": self.logical_step,
            "goals": [item.to_dict() for item in self.goals],
            "needs": [item.to_dict() for item in self.needs],
            "beliefs": [item.to_dict() for item in self.beliefs],
            "predictions": [item.to_dict() for item in self.predictions],
            "memories": [item.to_dict() for item in self.memories],
            "possible_actions": [item.to_dict() for item in self.possible_actions],
            "uncertainty_ppm": self.uncertainty_ppm,
            "hard_constraint_ids": list(self.hard_constraint_ids),
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
