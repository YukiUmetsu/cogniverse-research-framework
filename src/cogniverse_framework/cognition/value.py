"""Value and hard-constraint contracts (F2 foundation)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, ClassVar

from ._validation import normalize_identifiers, normalize_opaque_identifiers, validate_identifier, validate_opaque_identifier, validate_ppm


class ConstraintScope(str, Enum):
    """Scopes for hard constraints — semantics injected by the lab."""

    SELF = "self"
    USER = "user"
    OTHER_INDIVIDUAL = "other_individual"
    GROUP = "group"
    HUMANITY = "humanity"
    ENVIRONMENT = "environment"
    SYSTEM = "system"


@dataclass(frozen=True, slots=True)
class HardConstraint:
    """A non-compensatable prohibition separate from soft value."""

    SCHEMA_VERSION: ClassVar[str] = "hard_constraint.v1"

    constraint_id: str
    source_system: str
    logical_step: int
    scopes: tuple[ConstraintScope, ...] = field(default_factory=tuple)
    blocked_subject_ids: tuple[str, ...] = field(default_factory=tuple)
    description_sha256: str | None = None
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("constraint_id", self.constraint_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        normalized_scopes = tuple(
            sorted(
                (ConstraintScope(item) if not isinstance(item, ConstraintScope) else item for item in self.scopes),
                key=lambda item: item.value,
            )
        )
        object.__setattr__(self, "scopes", normalized_scopes)
        object.__setattr__(
            self,
            "blocked_subject_ids",
            normalize_identifiers("blocked_subject_ids", tuple(self.blocked_subject_ids)),
        )
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "constraint_id": self.constraint_id,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "scopes": [scope.value for scope in self.scopes],
            "blocked_subject_ids": list(self.blocked_subject_ids),
            "description_sha256": self.description_sha256,
            "evidence_ids": list(self.evidence_ids),
        }

    def digest(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()


@dataclass(frozen=True, slots=True)
class ConstraintViolation:
    """Record of a hard-constraint breach attempt or outcome."""

    SCHEMA_VERSION: ClassVar[str] = "constraint_violation.v1"

    violation_id: str
    constraint_id: str
    source_system: str
    logical_step: int
    subject_id: str
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("violation_id", self.violation_id)
        validate_identifier("constraint_id", self.constraint_id)
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
            "violation_id": self.violation_id,
            "constraint_id": self.constraint_id,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "subject_id": self.subject_id,
            "evidence_ids": list(self.evidence_ids),
        }


@dataclass(frozen=True, slots=True)
class ValueVector:
    """Multidimensional soft value estimate keyed by opaque dimension ids."""

    SCHEMA_VERSION: ClassVar[str] = "value_vector.v1"

    vector_id: str
    source_system: str
    logical_step: int
    dimension_values_ppm: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("vector_id", self.vector_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        normalized_pairs: list[tuple[str, int]] = []
        for dimension_id, value_ppm in self.dimension_values_ppm:
            validate_opaque_identifier("dimension_id", dimension_id)
            validate_ppm("dimension_value_ppm", value_ppm)
            normalized_pairs.append((dimension_id, value_ppm))
        object.__setattr__(
            self,
            "dimension_values_ppm",
            tuple(sorted(normalized_pairs, key=lambda item: item[0])),
        )
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )
        if any(dimension_id == "survival" for dimension_id, _ in self.dimension_values_ppm):
            raise ValueError(
                "survival dimension cannot be set directly on ValueVector; use NeedState/homeostasis contracts"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "vector_id": self.vector_id,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "dimension_values_ppm": [
                {"dimension_id": dimension_id, "value_ppm": value_ppm}
                for dimension_id, value_ppm in self.dimension_values_ppm
            ],
            "evidence_ids": list(self.evidence_ids),
        }

    def digest(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()


@dataclass(frozen=True, slots=True)
class ValueEstimate:
    """Soft value estimate with uncertainty and planning horizon."""

    SCHEMA_VERSION: ClassVar[str] = "value_estimate.v1"

    estimate_id: str
    source_system: str
    logical_step: int
    value_vector: ValueVector
    uncertainty_ppm: int | None = None
    horizon_steps: int | None = None
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("estimate_id", self.estimate_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        validate_ppm("uncertainty_ppm", self.uncertainty_ppm)
        if self.horizon_steps is not None and (
            isinstance(self.horizon_steps, bool)
            or not isinstance(self.horizon_steps, int)
            or self.horizon_steps < 0
        ):
            raise ValueError("horizon_steps must be None or a non-negative integer")
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "estimate_id": self.estimate_id,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "value_vector": self.value_vector.to_dict(),
            "uncertainty_ppm": self.uncertainty_ppm,
            "horizon_steps": self.horizon_steps,
            "evidence_ids": list(self.evidence_ids),
        }
