"""Environment-neutral typed output boundary for perception systems.

The contract identifies public perceptual content without embedding raw payloads,
task semantics, natural-language control, or a belief commitment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import re
from typing import Any, ClassVar

from ._validation import normalize_identifiers, validate_identifier, validate_ppm


_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class PerceptModality(str, Enum):
    """Broad signal family; environment-specific decoding stays outside the framework."""

    VISUAL = "visual"
    AUDITORY = "auditory"
    PROPRIOCEPTIVE = "proprioceptive"
    STRUCTURED = "structured"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class PublicPercept:
    """A provenance-bearing identity for one public perceptual record."""

    SCHEMA_VERSION: ClassVar[str] = "public_percept.v1"

    percept_id: str
    modality: PerceptModality
    source_system: str
    logical_step: int
    content_sha256: str
    confidence_ppm: int | None = None
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("percept_id", self.percept_id)
        validate_identifier("source_system", self.source_system)
        if isinstance(self.logical_step, bool) or not isinstance(self.logical_step, int) or self.logical_step < 0:
            raise ValueError("logical_step must be a non-negative integer")
        if not isinstance(self.modality, PerceptModality):
            raise ValueError("modality must be a PerceptModality")
        if not isinstance(self.content_sha256, str) or not _SHA256_PATTERN.fullmatch(self.content_sha256):
            raise ValueError("content_sha256 must be a lowercase SHA-256 hex digest")
        validate_ppm("confidence_ppm", self.confidence_ppm)
        evidence_ids = normalize_identifiers("evidence_ids", tuple(self.evidence_ids))
        if not evidence_ids:
            raise ValueError("evidence_ids must contain public provenance")
        object.__setattr__(self, "evidence_ids", evidence_ids)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "percept_id": self.percept_id,
            "modality": self.modality.value,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "content_sha256": self.content_sha256,
            "confidence_ppm": self.confidence_ppm,
            "evidence_ids": list(self.evidence_ids),
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()
