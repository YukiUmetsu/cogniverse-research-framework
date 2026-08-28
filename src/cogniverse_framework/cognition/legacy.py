"""Explicit legacy adapters for backward-compatible reward signals."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from ._validation import normalize_opaque_identifiers, validate_identifier, validate_ppm
from .value import ValueVector


@dataclass(frozen=True, slots=True)
class LegacyScalarRewardAdapter:
    """Map a scalar reward into an explicit, bounded value dimension.

    Scalar reward must not silently populate survival/safety/homeostasis fields.
    """

    SCHEMA_VERSION: ClassVar[str] = "legacy_scalar_reward_adapter.v1"

    adapter_id: str
    source_system: str
    logical_step: int
    target_dimension_id: str
    scale_ppm: int = 1_000_000

    def __post_init__(self) -> None:
        validate_identifier("adapter_id", self.adapter_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        normalize_opaque_identifiers("target_dimension_id", (self.target_dimension_id,))
        validate_ppm("scale_ppm", self.scale_ppm)
        forbidden = {"survival", "safety", "homeostasis"}
        if self.target_dimension_id in forbidden:
            raise ValueError(
                "legacy scalar reward cannot target survival, safety, or homeostasis dimensions"
            )

    def to_value_vector(
        self,
        *,
        vector_id: str,
        scalar_reward_ppm: int,
        evidence_ids: tuple[str, ...] = (),
    ) -> ValueVector:
        validate_ppm("scalar_reward_ppm", scalar_reward_ppm)
        scaled = min(
            1_000_000,
            max(0, (scalar_reward_ppm * self.scale_ppm) // 1_000_000),
        )
        return ValueVector(
            vector_id=vector_id,
            source_system=self.source_system,
            logical_step=self.logical_step,
            dimension_values_ppm=((self.target_dimension_id, scaled),),
            evidence_ids=evidence_ids,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "adapter_id": self.adapter_id,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "target_dimension_id": self.target_dimension_id,
            "scale_ppm": self.scale_ppm,
        }
