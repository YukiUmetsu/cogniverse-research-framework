"""Domain-agnostic per-seed audit cards and run-profile comparison.

Callers project domain worlds into ``SeedProfile`` objects. This module builds
versioned audit cards, contrasts one seed against a reference cohort, and
compares two runs seed-by-seed. Experiment claim wording stays outside.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .seed_diagnosis_types import SeedProfile

SEED_AUDIT_CARD_SCHEMA_VERSION = "seed_audit_card.v1"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _numeric(value: float | int | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _metric_delta(
    left: float | int | None, right: float | int | None
) -> float | None:
    if left is None or right is None:
        return None
    return float(left) - float(right)


def _l1_distance(left: SeedProfile, right: SeedProfile, metrics: Sequence[str]) -> float:
    total = 0.0
    counted = 0
    for name in metrics:
        a = _numeric(left.metrics.get(name))
        b = _numeric(right.metrics.get(name))
        if a is None or b is None:
            continue
        total += abs(a - b)
        counted += 1
    if counted == 0:
        return float("inf")
    return total


@dataclass(frozen=True)
class SeedAuditCard:
    """One seed's compact replay audit card."""

    schema_version: str
    seed: Any
    outcome: str | bool | None
    metrics: dict[str, float | int | None]
    milestones: dict[str, int | None]
    tags: dict[str, Any]
    failure_labels: tuple[str, ...] = ()
    reference_seed: Any | None = None
    metric_deltas_vs_reference: dict[str, float | None] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "seed": self.seed,
            "outcome": self.outcome,
            "metrics": dict(self.metrics),
            "milestones": dict(self.milestones),
            "tags": dict(self.tags),
            "failure_labels": list(self.failure_labels),
            "reference_seed": self.reference_seed,
            "metric_deltas_vs_reference": dict(self.metric_deltas_vs_reference),
        }


@dataclass(frozen=True)
class SeedReferenceContrast:
    """How one seed differs from its nearest reference profile."""

    seed: Any
    reference_seed: Any
    distance: float
    metric_deltas: dict[str, float | None]

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "reference_seed": self.reference_seed,
            "distance": self.distance,
            "metric_deltas": dict(self.metric_deltas),
        }


@dataclass(frozen=True)
class SeedAuditDelta:
    """Per-seed metric/milestone deltas between two run profiles."""

    seed: Any
    left_outcome: str | bool | None
    right_outcome: str | bool | None
    metric_deltas: dict[str, float | None]
    milestone_deltas: dict[str, int | None]
    left_only_milestones: tuple[str, ...]
    right_only_milestones: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "left_outcome": self.left_outcome,
            "right_outcome": self.right_outcome,
            "metric_deltas": dict(self.metric_deltas),
            "milestone_deltas": dict(self.milestone_deltas),
            "left_only_milestones": list(self.left_only_milestones),
            "right_only_milestones": list(self.right_only_milestones),
        }


def build_seed_audit_card(
    profile: SeedProfile,
    *,
    failure_labels: Sequence[str] = (),
    reference: SeedProfile | None = None,
    metrics: Sequence[str] | None = None,
) -> SeedAuditCard:
    """Build a versioned audit card from one ``SeedProfile``."""

    metric_names = tuple(metrics) if metrics is not None else tuple(sorted(profile.metrics))
    deltas: dict[str, float | None] = {}
    reference_seed = None
    if reference is not None:
        reference_seed = reference.seed
        for name in metric_names:
            deltas[name] = _metric_delta(
                profile.metrics.get(name), reference.metrics.get(name)
            )
    return SeedAuditCard(
        schema_version=SEED_AUDIT_CARD_SCHEMA_VERSION,
        seed=profile.seed,
        outcome=profile.outcome,
        metrics=dict(profile.metrics),
        milestones=dict(profile.milestones),
        tags=dict(profile.tags),
        failure_labels=tuple(failure_labels),
        reference_seed=reference_seed,
        metric_deltas_vs_reference=deltas,
    )


def contrast_seed_to_references(
    profile: SeedProfile,
    references: Sequence[SeedProfile],
    *,
    metrics: Sequence[str] | None = None,
) -> SeedReferenceContrast:
    """Contrast one seed against the nearest reference profile by L1 metric distance."""

    _require(bool(references), "references must be non-empty")
    metric_names = (
        tuple(metrics)
        if metrics is not None
        else tuple(sorted({*profile.metrics, *(m for ref in references for m in ref.metrics)}))
    )
    best: SeedProfile | None = None
    best_distance = float("inf")
    for reference in references:
        distance = _l1_distance(profile, reference, metric_names)
        if distance < best_distance:
            best = reference
            best_distance = distance
    assert best is not None
    deltas = {
        name: _metric_delta(profile.metrics.get(name), best.metrics.get(name))
        for name in metric_names
    }
    return SeedReferenceContrast(
        seed=profile.seed,
        reference_seed=best.seed,
        distance=float(best_distance) if best_distance != float("inf") else float("inf"),
        metric_deltas=deltas,
    )


def build_seed_audit_cards(
    profiles: Sequence[SeedProfile],
    *,
    reference_seeds: Sequence[Any] | None = None,
    failure_labels_by_seed: Mapping[Any, Sequence[str]] | None = None,
    metrics: Sequence[str] | None = None,
) -> tuple[SeedAuditCard, ...]:
    """Build audit cards for a run, optionally contrasting each seed to nearest reference."""

    indexed = {profile.seed: profile for profile in profiles}
    _require(len(indexed) == len(profiles), "duplicate seed profiles")
    if reference_seeds is None:
        references = tuple(
            profile
            for profile in profiles
            if profile.outcome in ("success", True, "pass", "PASS")
        )
    else:
        references = tuple(indexed[seed] for seed in reference_seeds if seed in indexed)
    labels = failure_labels_by_seed or {}
    cards: list[SeedAuditCard] = []
    for profile in profiles:
        reference = None
        if references and profile.seed not in {ref.seed for ref in references}:
            contrast = contrast_seed_to_references(
                profile, references, metrics=metrics
            )
            reference = indexed.get(contrast.reference_seed)
        cards.append(
            build_seed_audit_card(
                profile,
                failure_labels=tuple(labels.get(profile.seed, ())),
                reference=reference,
                metrics=metrics,
            )
        )
    return tuple(cards)


def compare_seed_audits(
    left: Sequence[SeedProfile],
    right: Sequence[SeedProfile],
    *,
    metrics: Sequence[str] | None = None,
    milestones: Sequence[str] | None = None,
) -> tuple[SeedAuditDelta, ...]:
    """Compare two runs seed-by-seed (right - left for numeric deltas)."""

    left_index = {profile.seed: profile for profile in left}
    right_index = {profile.seed: profile for profile in right}
    _require(len(left_index) == len(left), "duplicate seed in left profiles")
    _require(len(right_index) == len(right), "duplicate seed in right profiles")
    shared = sorted(
        set(left_index) & set(right_index),
        key=lambda seed: (str(type(seed)), str(seed)),
    )
    metric_names = (
        tuple(metrics)
        if metrics is not None
        else tuple(
            sorted(
                {
                    *{name for profile in left for name in profile.metrics},
                    *{name for profile in right for name in profile.metrics},
                }
            )
        )
    )
    milestone_names = (
        tuple(milestones)
        if milestones is not None
        else tuple(
            sorted(
                {
                    *{name for profile in left for name in profile.milestones},
                    *{name for profile in right for name in profile.milestones},
                }
            )
        )
    )
    deltas: list[SeedAuditDelta] = []
    for seed in shared:
        left_profile = left_index[seed]
        right_profile = right_index[seed]
        metric_deltas = {
            name: _metric_delta(
                right_profile.metrics.get(name), left_profile.metrics.get(name)
            )
            for name in metric_names
        }
        milestone_deltas: dict[str, int | None] = {}
        left_only: list[str] = []
        right_only: list[str] = []
        for name in milestone_names:
            left_value = left_profile.milestones.get(name)
            right_value = right_profile.milestones.get(name)
            if left_value is None and right_value is None:
                milestone_deltas[name] = None
            elif left_value is None and right_value is not None:
                right_only.append(name)
                milestone_deltas[name] = None
            elif left_value is not None and right_value is None:
                left_only.append(name)
                milestone_deltas[name] = None
            else:
                assert left_value is not None and right_value is not None
                milestone_deltas[name] = int(right_value) - int(left_value)
        deltas.append(
            SeedAuditDelta(
                seed=seed,
                left_outcome=left_profile.outcome,
                right_outcome=right_profile.outcome,
                metric_deltas=metric_deltas,
                milestone_deltas=milestone_deltas,
                left_only_milestones=tuple(left_only),
                right_only_milestones=tuple(right_only),
            )
        )
    return tuple(deltas)
