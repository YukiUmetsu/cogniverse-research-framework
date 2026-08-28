"""Working and primed memory contracts for bounded active cognition."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, ClassVar

from .._validation import validate_identifier, validate_ppm
from .activation import ActivationReason


@dataclass(frozen=True, slots=True)
class WorkingMemoryItem:
    """One node admitted into bounded working memory."""

    SCHEMA_VERSION: ClassVar[str] = "working_memory_item.v1"

    node_id: str
    admitted_at_step: int
    admission_reason: ActivationReason
    activation_ppm_at_admission: int

    def __post_init__(self) -> None:
        validate_identifier("node_id", self.node_id)
        if (
            isinstance(self.admitted_at_step, bool)
            or not isinstance(self.admitted_at_step, int)
            or self.admitted_at_step < 0
        ):
            raise ValueError("admitted_at_step must be a non-negative integer")
        validate_ppm("activation_ppm_at_admission", self.activation_ppm_at_admission)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "node_id": self.node_id,
            "admitted_at_step": self.admitted_at_step,
            "admission_reason": self.admission_reason.value,
            "activation_ppm_at_admission": self.activation_ppm_at_admission,
        }


@dataclass(frozen=True, slots=True)
class PrimedMemoryItem:
    """A partially activated candidate not consuming working-memory capacity."""

    SCHEMA_VERSION: ClassVar[str] = "primed_memory_item.v1"

    node_id: str
    primed_at_step: int
    activation_ppm: int
    admission_reason: ActivationReason

    def __post_init__(self) -> None:
        validate_identifier("node_id", self.node_id)
        if (
            isinstance(self.primed_at_step, bool)
            or not isinstance(self.primed_at_step, int)
            or self.primed_at_step < 0
        ):
            raise ValueError("primed_at_step must be a non-negative integer")
        validate_ppm("activation_ppm", self.activation_ppm)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "node_id": self.node_id,
            "primed_at_step": self.primed_at_step,
            "activation_ppm": self.activation_ppm,
            "admission_reason": self.admission_reason.value,
        }


@dataclass(frozen=True, slots=True)
class MemoryEvictionRecord:
    """Trace of a node removed from working memory."""

    SCHEMA_VERSION: ClassVar[str] = "memory_eviction_record.v1"

    node_id: str
    logical_step: int
    reason: ActivationReason
    activation_ppm: int

    def __post_init__(self) -> None:
        validate_identifier("node_id", self.node_id)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        validate_ppm("activation_ppm", self.activation_ppm)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "node_id": self.node_id,
            "logical_step": self.logical_step,
            "reason": self.reason.value,
            "activation_ppm": self.activation_ppm,
        }


@dataclass(frozen=True, slots=True)
class WorkingMemory:
    """Bounded set of nodes actively participating in cognition."""

    SCHEMA_VERSION: ClassVar[str] = "working_memory.v1"

    capacity: int
    items: tuple[WorkingMemoryItem, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not isinstance(self.capacity, int) or self.capacity < 1:
            raise ValueError("capacity must be a positive integer")
        sorted_items = tuple(sorted(self.items, key=lambda item: item.node_id))
        object.__setattr__(self, "items", sorted_items)
        node_ids = [item.node_id for item in sorted_items]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("working memory node_id values must be unique")
        if len(sorted_items) > self.capacity:
            raise ValueError("working memory exceeds configured capacity")

    def node_ids(self) -> tuple[str, ...]:
        return tuple(item.node_id for item in self.items)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "capacity": self.capacity,
            "items": [item.to_dict() for item in self.items],
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


@dataclass(frozen=True, slots=True)
class PrimedMemory:
    """Candidates associated with the situation but outside working memory."""

    SCHEMA_VERSION: ClassVar[str] = "primed_memory.v1"

    items: tuple[PrimedMemoryItem, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        sorted_items = tuple(sorted(self.items, key=lambda item: item.node_id))
        object.__setattr__(self, "items", sorted_items)
        node_ids = [item.node_id for item in sorted_items]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("primed memory node_id values must be unique")

    def node_ids(self) -> tuple[str, ...]:
        return tuple(item.node_id for item in self.items)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "items": [item.to_dict() for item in self.items],
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
