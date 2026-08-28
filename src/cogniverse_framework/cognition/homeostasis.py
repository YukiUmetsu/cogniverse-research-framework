"""Homeostasis and need-state contracts (F2 foundation)."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, ClassVar

from ._validation import normalize_identifiers, normalize_opaque_identifiers, validate_identifier, validate_opaque_identifier, validate_ppm


@dataclass(frozen=True, slots=True)
class NeedState:
    """Descriptive need record with level, target, deficit and provenance."""

    SCHEMA_VERSION: ClassVar[str] = "need_state.v1"

    need_id: str
    source_system: str
    logical_step: int
    need_kind: str
    level_ppm: int
    target_ppm: int
    deficit_ppm: int
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("need_id", self.need_id)
        validate_identifier("source_system", self.source_system)
        validate_opaque_identifier("need_kind", self.need_kind)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        validate_ppm("level_ppm", self.level_ppm)
        validate_ppm("target_ppm", self.target_ppm)
        validate_ppm("deficit_ppm", self.deficit_ppm)
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "need_id": self.need_id,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "need_kind": self.need_kind,
            "level_ppm": self.level_ppm,
            "target_ppm": self.target_ppm,
            "deficit_ppm": self.deficit_ppm,
            "evidence_ids": list(self.evidence_ids),
        }

    def digest(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()


@dataclass(frozen=True, slots=True)
class HomeostaticUpdate:
    """Deterministic record of a homeostatic state transition."""

    SCHEMA_VERSION: ClassVar[str] = "homeostatic_update.v1"

    update_id: str
    source_system: str
    logical_step: int
    need_id: str
    previous_level_ppm: int
    new_level_ppm: int
    previous_deficit_ppm: int
    new_deficit_ppm: int
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("update_id", self.update_id)
        validate_identifier("source_system", self.source_system)
        validate_identifier("need_id", self.need_id)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        for name in (
            "previous_level_ppm",
            "new_level_ppm",
            "previous_deficit_ppm",
            "new_deficit_ppm",
        ):
            validate_ppm(name, getattr(self, name))
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "update_id": self.update_id,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "need_id": self.need_id,
            "previous_level_ppm": self.previous_level_ppm,
            "new_level_ppm": self.new_level_ppm,
            "previous_deficit_ppm": self.previous_deficit_ppm,
            "new_deficit_ppm": self.new_deficit_ppm,
            "evidence_ids": list(self.evidence_ids),
        }
