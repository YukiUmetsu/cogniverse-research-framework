"""Replay helpers for value and homeostasis mechanism traces (F2)."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, ClassVar, Iterable

from cogniverse_framework.cognition.constraints import ConstraintEvaluation
from cogniverse_framework.cognition.homeostasis import HomeostaticUpdate, NeedState
from cogniverse_framework.cognition.priority import RankedNeed
from cogniverse_framework.cognition.value import ConstraintViolation, ValueEstimate, ValueVector


def _constraint_evaluation_sort_key(item: ConstraintEvaluation) -> tuple[str | int | bool, ...]:
    return (
        item.subject_id,
        item.logical_step,
        item.source_system,
        item.allowed,
        tuple(violation.violation_id for violation in item.violations),
    )


def _value_vector_from_dict(payload: dict[str, Any]) -> ValueVector:
    return ValueVector(
        vector_id=payload["vector_id"],
        source_system=payload["source_system"],
        logical_step=payload["logical_step"],
        dimension_values_ppm=tuple(
            (pair["dimension_id"], pair["value_ppm"])
            for pair in payload.get("dimension_values_ppm", ())
        ),
        evidence_ids=tuple(payload.get("evidence_ids", ())),
    )


def _value_estimate_from_dict(payload: dict[str, Any]) -> ValueEstimate:
    return ValueEstimate(
        estimate_id=payload["estimate_id"],
        source_system=payload["source_system"],
        logical_step=payload["logical_step"],
        value_vector=_value_vector_from_dict(payload["value_vector"]),
        uncertainty_ppm=payload.get("uncertainty_ppm"),
        horizon_steps=payload.get("horizon_steps"),
        evidence_ids=tuple(payload.get("evidence_ids", ())),
    )


def _constraint_evaluation_from_dict(payload: dict[str, Any]) -> ConstraintEvaluation:
    return ConstraintEvaluation(
        subject_id=payload["subject_id"],
        logical_step=payload["logical_step"],
        source_system=payload["source_system"],
        allowed=payload["allowed"],
        violations=tuple(
            ConstraintViolation(
                violation_id=item["violation_id"],
                constraint_id=item["constraint_id"],
                source_system=item["source_system"],
                logical_step=item["logical_step"],
                subject_id=item["subject_id"],
                evidence_ids=tuple(item.get("evidence_ids", ())),
            )
            for item in payload.get("violations", ())
        ),
    )


def _need_state_from_dict(payload: dict[str, Any]) -> NeedState:
    return NeedState(
        need_id=payload["need_id"],
        source_system=payload["source_system"],
        logical_step=payload["logical_step"],
        need_kind=payload["need_kind"],
        level_ppm=payload["level_ppm"],
        target_ppm=payload["target_ppm"],
        deficit_ppm=payload["deficit_ppm"],
        evidence_ids=tuple(payload.get("evidence_ids", ())),
    )


def _ranked_need_from_dict(payload: dict[str, Any]) -> RankedNeed:
    return RankedNeed(
        need=_need_state_from_dict(payload["need"]),
        weight_ppm=payload["weight_ppm"],
        priority_score_ppm=payload["priority_score_ppm"],
    )


@dataclass(frozen=True, slots=True)
class ValueHomeostasisTrace:
    """Deterministic auditable trace of F2 mechanism records."""

    SCHEMA_VERSION: ClassVar[str] = "value_homeostasis_trace.v1"

    source_system: str
    logical_step: int
    need_states: tuple[NeedState, ...] = field(default_factory=tuple)
    homeostatic_updates: tuple[HomeostaticUpdate, ...] = field(default_factory=tuple)
    value_vectors: tuple[ValueVector, ...] = field(default_factory=tuple)
    value_estimates: tuple[ValueEstimate, ...] = field(default_factory=tuple)
    constraint_evaluations: tuple[ConstraintEvaluation, ...] = field(default_factory=tuple)
    ranked_needs: tuple[RankedNeed, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        object.__setattr__(
            self,
            "need_states",
            tuple(sorted(self.need_states, key=lambda item: item.need_id)),
        )
        object.__setattr__(
            self,
            "homeostatic_updates",
            tuple(sorted(self.homeostatic_updates, key=lambda item: item.update_id)),
        )
        object.__setattr__(
            self,
            "value_vectors",
            tuple(sorted(self.value_vectors, key=lambda item: item.vector_id)),
        )
        object.__setattr__(
            self,
            "value_estimates",
            tuple(sorted(self.value_estimates, key=lambda item: item.estimate_id)),
        )
        object.__setattr__(
            self,
            "constraint_evaluations",
            tuple(
                sorted(
                    self.constraint_evaluations,
                    key=_constraint_evaluation_sort_key,
                )
            ),
        )
        object.__setattr__(
            self,
            "ranked_needs",
            tuple(
                sorted(
                    self.ranked_needs,
                    key=lambda item: (-item.priority_score_ppm, item.need.need_id),
                )
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "need_states": [item.to_dict() for item in self.need_states],
            "homeostatic_updates": [item.to_dict() for item in self.homeostatic_updates],
            "value_vectors": [item.to_dict() for item in self.value_vectors],
            "value_estimates": [item.to_dict() for item in self.value_estimates],
            "constraint_evaluations": [item.to_dict() for item in self.constraint_evaluations],
            "ranked_needs": [
                {
                    "need": item.need.to_dict(),
                    "weight_ppm": item.weight_ppm,
                    "priority_score_ppm": item.priority_score_ppm,
                }
                for item in self.ranked_needs
            ],
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
    def from_dict(cls, payload: dict[str, Any]) -> ValueHomeostasisTrace:
        return cls(
            source_system=payload["source_system"],
            logical_step=payload["logical_step"],
            need_states=tuple(
                _need_state_from_dict(item) for item in payload.get("need_states", ())
            ),
            homeostatic_updates=tuple(
                HomeostaticUpdate(
                    update_id=item["update_id"],
                    source_system=item["source_system"],
                    logical_step=item["logical_step"],
                    need_id=item["need_id"],
                    previous_level_ppm=item["previous_level_ppm"],
                    new_level_ppm=item["new_level_ppm"],
                    previous_deficit_ppm=item["previous_deficit_ppm"],
                    new_deficit_ppm=item["new_deficit_ppm"],
                    evidence_ids=tuple(item.get("evidence_ids", ())),
                )
                for item in payload.get("homeostatic_updates", ())
            ),
            value_vectors=tuple(
                _value_vector_from_dict(item) for item in payload.get("value_vectors", ())
            ),
            value_estimates=tuple(
                _value_estimate_from_dict(item)
                for item in payload.get("value_estimates", ())
            ),
            constraint_evaluations=tuple(
                _constraint_evaluation_from_dict(item)
                for item in payload.get("constraint_evaluations", ())
            ),
            ranked_needs=tuple(
                _ranked_need_from_dict(item) for item in payload.get("ranked_needs", ())
            ),
        )


def build_value_homeostasis_trace(
    *,
    source_system: str,
    logical_step: int,
    need_states: Iterable[NeedState] = (),
    homeostatic_updates: Iterable[HomeostaticUpdate] = (),
    value_vectors: Iterable[ValueVector] = (),
    value_estimates: Iterable[ValueEstimate] = (),
    constraint_evaluations: Iterable[ConstraintEvaluation] = (),
    ranked_needs: Iterable[RankedNeed] = (),
) -> ValueHomeostasisTrace:
    return ValueHomeostasisTrace(
        source_system=source_system,
        logical_step=logical_step,
        need_states=tuple(need_states),
        homeostatic_updates=tuple(homeostatic_updates),
        value_vectors=tuple(value_vectors),
        value_estimates=tuple(value_estimates),
        constraint_evaluations=tuple(constraint_evaluations),
        ranked_needs=tuple(ranked_needs),
    )


def value_homeostasis_trace_to_evidence_payload(
    trace: ValueHomeostasisTrace,
) -> dict[str, Any]:
    """Serialize a value/homeostasis trace for lab evidence storage."""

    return {
        "artifact_kind": "value_homeostasis_trace",
        "trace_digest": trace.digest(),
        "trace": trace.to_dict(),
    }
