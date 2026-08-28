"""Long-term memory record references with distinct cognitive roles."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Any, ClassVar

from .._validation import normalize_identifiers, validate_identifier, validate_ppm
from ..state import MemoryKind


_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class LongTermMemoryRecord:
    """Environment-neutral reference to durable memory content owned elsewhere."""

    SCHEMA_VERSION: ClassVar[str] = "long_term_memory_record.v1"

    memory_id: str
    memory_kind: MemoryKind
    source_system: str
    logical_step: int
    content_sha256: str
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    related_node_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("memory_id", self.memory_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        if not _SHA256_PATTERN.fullmatch(self.content_sha256):
            raise ValueError("content_sha256 must be a lowercase SHA-256 hex digest")
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )
        if not self.evidence_ids:
            raise ValueError("evidence_ids must contain provenance references")
        related = normalize_identifiers(
            "related_node_ids", tuple(self.related_node_ids)
        )
        object.__setattr__(self, "related_node_ids", related)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "memory_id": self.memory_id,
            "memory_kind": self.memory_kind.value,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "content_sha256": self.content_sha256,
            "evidence_ids": list(self.evidence_ids),
            "related_node_ids": list(self.related_node_ids),
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


def episodic_memory_record(
    *,
    memory_id: str,
    source_system: str,
    logical_step: int,
    content_sha256: str,
    evidence_ids: tuple[str, ...] = (),
    related_node_ids: tuple[str, ...] = (),
) -> LongTermMemoryRecord:
    return LongTermMemoryRecord(
        memory_id=memory_id,
        memory_kind=MemoryKind.EPISODIC,
        source_system=source_system,
        logical_step=logical_step,
        content_sha256=content_sha256,
        evidence_ids=evidence_ids,
        related_node_ids=related_node_ids,
    )


def semantic_memory_record(
    *,
    memory_id: str,
    source_system: str,
    logical_step: int,
    content_sha256: str,
    evidence_ids: tuple[str, ...] = (),
    related_node_ids: tuple[str, ...] = (),
) -> LongTermMemoryRecord:
    return LongTermMemoryRecord(
        memory_id=memory_id,
        memory_kind=MemoryKind.SEMANTIC,
        source_system=source_system,
        logical_step=logical_step,
        content_sha256=content_sha256,
        evidence_ids=evidence_ids,
        related_node_ids=related_node_ids,
    )


def procedural_memory_record(
    *,
    memory_id: str,
    source_system: str,
    logical_step: int,
    content_sha256: str,
    evidence_ids: tuple[str, ...] = (),
    related_node_ids: tuple[str, ...] = (),
) -> LongTermMemoryRecord:
    return LongTermMemoryRecord(
        memory_id=memory_id,
        memory_kind=MemoryKind.PROCEDURAL,
        source_system=source_system,
        logical_step=logical_step,
        content_sha256=content_sha256,
        evidence_ids=evidence_ids,
        related_node_ids=related_node_ids,
    )


# Compatibility aliases for role-specific construction at call sites.
EpisodicMemoryRecord = episodic_memory_record
SemanticMemoryRecord = semantic_memory_record
ProceduralMemoryRecord = procedural_memory_record
