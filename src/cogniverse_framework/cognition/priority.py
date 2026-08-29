"""Transparent reference priority policies for homeostasis (F2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Iterable

from ._validation import normalize_opaque_identifiers, validate_identifier, validate_ppm
from .constraints import ConstraintEvaluation, evaluate_hard_constraints
from .homeostasis import NeedState
from .value import HardConstraint, ValueVector


@dataclass(frozen=True, slots=True)
class TransparentPriorityPolicy:
    """Injected ppm weights for need-kind priority ranking."""

    SCHEMA_VERSION: ClassVar[str] = "transparent_priority_policy.v1"

    policy_id: str
    source_system: str
    need_kind_weights_ppm: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    default_weight_ppm: int = 100_000

    def __post_init__(self) -> None:
        validate_identifier("policy_id", self.policy_id)
        validate_identifier("source_system", self.source_system)
        validate_ppm("default_weight_ppm", self.default_weight_ppm)
        normalized: list[tuple[str, int]] = []
        for need_kind, weight_ppm in self.need_kind_weights_ppm:
            validate_ppm("need_kind_weight_ppm", weight_ppm)
            normalized.append((need_kind, weight_ppm))
        object.__setattr__(
            self,
            "need_kind_weights_ppm",
            tuple(sorted(normalized, key=lambda item: item[0])),
        )
        normalize_opaque_identifiers(
            "need_kind_weights_ppm",
            tuple(kind for kind, _ in self.need_kind_weights_ppm),
        )

    def weight_for(self, need_kind: str) -> int:
        for kind, weight_ppm in self.need_kind_weights_ppm:
            if kind == need_kind:
                return weight_ppm
        return self.default_weight_ppm

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "policy_id": self.policy_id,
            "source_system": self.source_system,
            "need_kind_weights_ppm": [
                {"need_kind": need_kind, "weight_ppm": weight_ppm}
                for need_kind, weight_ppm in self.need_kind_weights_ppm
            ],
            "default_weight_ppm": self.default_weight_ppm,
        }


@dataclass(frozen=True, slots=True)
class RankedNeed:
    """One need with transparent priority score components."""

    need: NeedState
    weight_ppm: int
    priority_score_ppm: int


def rank_need_states(
    needs: Iterable[NeedState],
    policy: TransparentPriorityPolicy,
) -> tuple[RankedNeed, ...]:
    """Rank needs by deficit × injected weight (deterministic tie-break on need_id)."""

    ranked: list[RankedNeed] = []
    for need in needs:
        weight_ppm = policy.weight_for(need.need_kind)
        priority_score_ppm = min(
            1_000_000,
            (need.deficit_ppm * weight_ppm) // 1_000_000,
        )
        ranked.append(
            RankedNeed(
                need=need,
                weight_ppm=weight_ppm,
                priority_score_ppm=priority_score_ppm,
            )
        )
    return tuple(
        sorted(
            ranked,
            key=lambda item: (-item.priority_score_ppm, item.need.need_id),
        )
    )


def evaluate_subject_with_constraints(
    constraints: Iterable[HardConstraint],
    *,
    subject_id: str,
    logical_step: int,
    source_system: str,
    evidence_ids: tuple[str, ...] = (),
) -> ConstraintEvaluation:
    """Hard-constraint gate evaluated before soft value or need ranking."""

    return evaluate_hard_constraints(
        constraints,
        subject_id=subject_id,
        logical_step=logical_step,
        source_system=source_system,
        evidence_ids=evidence_ids,
    )


def rank_value_vectors(
    vectors: Iterable[ValueVector],
) -> tuple[ValueVector, ...]:
    """Deterministic soft-value ordering by summed dimension ppm."""

    def total_ppm(vector: ValueVector) -> int:
        return sum(value_ppm for _, value_ppm in vector.dimension_values_ppm)

    return tuple(
        sorted(
            vectors,
            key=lambda item: (-total_ppm(item), item.vector_id),
        )
    )
