"""Retrieval request and result contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, ClassVar

from .._validation import normalize_identifiers, validate_identifier, validate_ppm
from ..state import MemoryKind
from .gaps import CognitiveGap
from .signals import RetrievalScoreComponent


@dataclass(frozen=True, slots=True)
class RetrievalRequest:
    """Typed request to search long-term memory for gap-relevant information."""

    SCHEMA_VERSION: ClassVar[str] = "retrieval_request.v1"

    request_id: str
    logical_step: int
    source_system: str
    gap: CognitiveGap
    memory_roles: tuple[MemoryKind, ...]
    budget: int
    active_graph_digest: str | None = None
    goal_node_ids: tuple[str, ...] = field(default_factory=tuple)
    primed_node_ids: tuple[str, ...] = field(default_factory=tuple)
    working_node_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("request_id", self.request_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        if isinstance(self.budget, bool) or not isinstance(self.budget, int) or self.budget < 1:
            raise ValueError("budget must be a positive integer")
        if not self.memory_roles:
            raise ValueError("memory_roles must contain at least one role")
        roles = tuple(sorted(set(self.memory_roles), key=lambda role: role.value))
        object.__setattr__(self, "memory_roles", roles)
        object.__setattr__(
            self,
            "goal_node_ids",
            normalize_identifiers("goal_node_ids", tuple(self.goal_node_ids)),
        )
        object.__setattr__(
            self,
            "primed_node_ids",
            normalize_identifiers("primed_node_ids", tuple(self.primed_node_ids)),
        )
        object.__setattr__(
            self,
            "working_node_ids",
            normalize_identifiers("working_node_ids", tuple(self.working_node_ids)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "request_id": self.request_id,
            "logical_step": self.logical_step,
            "source_system": self.source_system,
            "gap": self.gap.to_dict(),
            "memory_roles": [role.value for role in self.memory_roles],
            "budget": self.budget,
            "active_graph_digest": self.active_graph_digest,
            "goal_node_ids": list(self.goal_node_ids),
            "primed_node_ids": list(self.primed_node_ids),
            "working_node_ids": list(self.working_node_ids),
        }


@dataclass(frozen=True, slots=True)
class RetrievalCandidate:
    """One ranked memory candidate returned by retrieval."""

    SCHEMA_VERSION: ClassVar[str] = "retrieval_candidate.v1"

    memory_id: str
    memory_kind: MemoryKind
    score_ppm: int
    score_components: tuple[RetrievalScoreComponent, ...]
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("memory_id", self.memory_id)
        validate_ppm("score_ppm", self.score_ppm)
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )
        sorted_components = tuple(
            sorted(self.score_components, key=lambda item: item.signal.value)
        )
        object.__setattr__(self, "score_components", sorted_components)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "memory_id": self.memory_id,
            "memory_kind": self.memory_kind.value,
            "score_ppm": self.score_ppm,
            "score_components": [item.to_dict() for item in self.score_components],
            "evidence_ids": list(self.evidence_ids),
        }


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """Outcome of one retrieval request with ranked candidates."""

    SCHEMA_VERSION: ClassVar[str] = "retrieval_result.v1"

    request_id: str
    logical_step: int
    source_system: str
    gap_id: str
    candidates: tuple[RetrievalCandidate, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("request_id", self.request_id)
        validate_identifier("gap_id", self.gap_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        sorted_candidates = tuple(
            sorted(
                self.candidates,
                key=lambda item: (-item.score_ppm, item.memory_id, item.memory_kind.value),
            )
        )
        object.__setattr__(self, "candidates", sorted_candidates)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "request_id": self.request_id,
            "logical_step": self.logical_step,
            "source_system": self.source_system,
            "gap_id": self.gap_id,
            "candidates": [item.to_dict() for item in self.candidates],
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
