"""Typed results for seed-failure diagnosis.

Framework infrastructure: callers supply per-seed metric profiles. Experiment
labels and scientific interpretation stay in the learning lab.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SeedProfile:
    """One seed's replay-derived metric profile.

    ``metrics`` hold numeric coverage/budget signals.
    ``milestones`` hold first-index timings for named events (or None if absent).
    ``outcome`` is caller-defined (commonly ``\"success\"`` / ``\"failure\"``).
    """

    seed: Any
    metrics: dict[str, float | int | None] = field(default_factory=dict)
    milestones: dict[str, int | None] = field(default_factory=dict)
    outcome: str | bool | None = None
    tags: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "metrics": dict(self.metrics),
            "milestones": dict(self.milestones),
            "outcome": self.outcome,
            "tags": dict(self.tags),
        }


@dataclass(frozen=True)
class MetricContrast:
    """How one metric differs between hard seeds and a reference cohort."""

    metric: str
    hard_median: float | None
    reference_median: float | None
    hard_min: float | None
    hard_max: float | None
    reference_min: float | None
    reference_max: float | None
    delta_median: float | None
    hard_strictly_below_reference: bool
    hard_strictly_above_reference: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "hard_median": self.hard_median,
            "reference_median": self.reference_median,
            "hard_min": self.hard_min,
            "hard_max": self.hard_max,
            "reference_min": self.reference_min,
            "reference_max": self.reference_max,
            "delta_median": self.delta_median,
            "hard_strictly_below_reference": self.hard_strictly_below_reference,
            "hard_strictly_above_reference": self.hard_strictly_above_reference,
        }


@dataclass(frozen=True)
class MilestoneContrast:
    """Presence and timing gaps for a named milestone."""

    milestone: str
    hard_present_count: int
    reference_present_count: int
    hard_median_index: float | None
    reference_median_index: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "milestone": self.milestone,
            "hard_present_count": self.hard_present_count,
            "reference_present_count": self.reference_present_count,
            "hard_median_index": self.hard_median_index,
            "reference_median_index": self.reference_median_index,
        }


@dataclass(frozen=True)
class SeedFailureDiagnosis:
    """Replay-only diagnosis of why selected seeds keep failing."""

    hard_seeds: tuple[Any, ...]
    reference_seeds: tuple[Any, ...]
    hard_profiles: tuple[SeedProfile, ...]
    reference_profiles: tuple[SeedProfile, ...]
    metric_contrasts: tuple[MetricContrast, ...]
    milestone_contrasts: tuple[MilestoneContrast, ...]
    separating_lower_metrics: tuple[str, ...]
    separating_higher_metrics: tuple[str, ...]
    classifier_labels: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "hard_seeds": list(self.hard_seeds),
            "reference_seeds": list(self.reference_seeds),
            "hard_profiles": [profile.to_dict() for profile in self.hard_profiles],
            "reference_profiles": [
                profile.to_dict() for profile in self.reference_profiles
            ],
            "metric_contrasts": [
                contrast.to_dict() for contrast in self.metric_contrasts
            ],
            "milestone_contrasts": [
                contrast.to_dict() for contrast in self.milestone_contrasts
            ],
            "separating_lower_metrics": list(self.separating_lower_metrics),
            "separating_higher_metrics": list(self.separating_higher_metrics),
            "classifier_labels": list(self.classifier_labels),
        }
