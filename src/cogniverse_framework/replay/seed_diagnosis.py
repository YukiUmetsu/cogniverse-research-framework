"""Replay-only diagnosis of repeatedly failing seeds.

Generic infrastructure: callers supply per-seed metric profiles (coverage,
budgets, milestone timings). The framework contrasts hard seeds against a
reference cohort and reports which metrics cleanly separate them.

Experiment-specific feature extraction and scientific claim wording belong in
the learning lab.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from statistics import median
from typing import Any

from .seed_diagnosis_types import (
    MetricContrast,
    MilestoneContrast,
    SeedFailureDiagnosis,
    SeedProfile,
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _median(values: Sequence[float | int | None]) -> float | None:
    present = [float(value) for value in values if value is not None]
    return float(median(present)) if present else None


def _min(values: Sequence[float | int | None]) -> float | None:
    present = [float(value) for value in values if value is not None]
    return min(present) if present else None


def _max(values: Sequence[float | int | None]) -> float | None:
    present = [float(value) for value in values if value is not None]
    return max(present) if present else None


def _index_profiles(
    profiles: Sequence[SeedProfile],
) -> dict[Any, SeedProfile]:
    indexed: dict[Any, SeedProfile] = {}
    for profile in profiles:
        _require(profile.seed not in indexed, f"duplicate seed profile: {profile.seed}")
        indexed[profile.seed] = profile
    return indexed


def _metric_names(
    profiles: Sequence[SeedProfile],
    requested: Sequence[str] | None,
) -> tuple[str, ...]:
    if requested is not None:
        return tuple(requested)
    names: set[str] = set()
    for profile in profiles:
        names.update(profile.metrics)
    return tuple(sorted(names))


def _milestone_names(
    profiles: Sequence[SeedProfile],
    requested: Sequence[str] | None,
) -> tuple[str, ...]:
    if requested is not None:
        return tuple(requested)
    names: set[str] = set()
    for profile in profiles:
        names.update(profile.milestones)
    return tuple(sorted(names))


def contrast_metric(
    metric: str,
    hard: Sequence[SeedProfile],
    reference: Sequence[SeedProfile],
) -> MetricContrast:
    hard_values = [profile.metrics.get(metric) for profile in hard]
    reference_values = [profile.metrics.get(metric) for profile in reference]
    hard_median = _median(hard_values)
    reference_median = _median(reference_values)
    hard_min = _min(hard_values)
    hard_max = _max(hard_values)
    reference_min = _min(reference_values)
    reference_max = _max(reference_values)
    delta = (
        None
        if hard_median is None or reference_median is None
        else float(hard_median - reference_median)
    )
    strictly_below = (
        hard_max is not None
        and reference_min is not None
        and hard_max < reference_min
    )
    strictly_above = (
        hard_min is not None
        and reference_max is not None
        and hard_min > reference_max
    )
    return MetricContrast(
        metric=metric,
        hard_median=hard_median,
        reference_median=reference_median,
        hard_min=hard_min,
        hard_max=hard_max,
        reference_min=reference_min,
        reference_max=reference_max,
        delta_median=delta,
        hard_strictly_below_reference=bool(strictly_below),
        hard_strictly_above_reference=bool(strictly_above),
    )


def contrast_milestone(
    milestone: str,
    hard: Sequence[SeedProfile],
    reference: Sequence[SeedProfile],
) -> MilestoneContrast:
    hard_values = [profile.milestones.get(milestone) for profile in hard]
    reference_values = [profile.milestones.get(milestone) for profile in reference]
    return MilestoneContrast(
        milestone=milestone,
        hard_present_count=sum(value is not None for value in hard_values),
        reference_present_count=sum(value is not None for value in reference_values),
        hard_median_index=_median(hard_values),
        reference_median_index=_median(reference_values),
    )


Classifier = Callable[
    [SeedFailureDiagnosis],
    str | None,
]


def diagnose_seed_failures(
    profiles: Sequence[SeedProfile],
    *,
    hard_seeds: Sequence[Any],
    reference_seeds: Sequence[Any] | None = None,
    metrics: Sequence[str] | None = None,
    milestones: Sequence[str] | None = None,
    classifiers: Sequence[Classifier] | None = None,
) -> SeedFailureDiagnosis:
    """Contrast repeatedly failing seeds against a reference cohort.

    Parameters
    ----------
    profiles:
        One profile per seed, built by the caller from archived evidence.
    hard_seeds:
        Seeds that keep failing and need explanation.
    reference_seeds:
        Comparison cohort. Defaults to every profiled seed not in ``hard_seeds``.
    metrics / milestones:
        Optional subsets; defaults to the union of keys present on profiles.
    classifiers:
        Optional callables that attach short labels after contrasts are computed.
        Classifiers must not mutate state; they return a label or ``None``.
    """

    indexed = _index_profiles(profiles)
    hard_list = list(hard_seeds)
    _require(hard_list, "hard_seeds must not be empty")
    for seed in hard_list:
        _require(seed in indexed, f"hard seed missing from profiles: {seed}")

    if reference_seeds is None:
        reference_list = [seed for seed in indexed if seed not in set(hard_list)]
    else:
        reference_list = list(reference_seeds)
        for seed in reference_list:
            _require(seed in indexed, f"reference seed missing from profiles: {seed}")
            _require(seed not in set(hard_list), f"seed in both cohorts: {seed}")
    _require(reference_list, "reference cohort must not be empty")

    hard_profiles = tuple(indexed[seed] for seed in hard_list)
    reference_profiles = tuple(indexed[seed] for seed in reference_list)
    selected_metrics = _metric_names(
        list(hard_profiles) + list(reference_profiles), metrics
    )
    selected_milestones = _milestone_names(
        list(hard_profiles) + list(reference_profiles), milestones
    )

    metric_contrasts = tuple(
        contrast_metric(name, hard_profiles, reference_profiles)
        for name in selected_metrics
    )
    milestone_contrasts = tuple(
        contrast_milestone(name, hard_profiles, reference_profiles)
        for name in selected_milestones
    )

    diagnosis = SeedFailureDiagnosis(
        hard_seeds=tuple(hard_list),
        reference_seeds=tuple(reference_list),
        hard_profiles=hard_profiles,
        reference_profiles=reference_profiles,
        metric_contrasts=metric_contrasts,
        milestone_contrasts=milestone_contrasts,
        separating_lower_metrics=tuple(
            contrast.metric
            for contrast in metric_contrasts
            if contrast.hard_strictly_below_reference
        ),
        separating_higher_metrics=tuple(
            contrast.metric
            for contrast in metric_contrasts
            if contrast.hard_strictly_above_reference
        ),
        classifier_labels=(),
    )

    if classifiers:
        labels: list[str] = []
        for classifier in classifiers:
            label = classifier(diagnosis)
            if label:
                labels.append(str(label))
        diagnosis = SeedFailureDiagnosis(
            hard_seeds=diagnosis.hard_seeds,
            reference_seeds=diagnosis.reference_seeds,
            hard_profiles=diagnosis.hard_profiles,
            reference_profiles=diagnosis.reference_profiles,
            metric_contrasts=diagnosis.metric_contrasts,
            milestone_contrasts=diagnosis.milestone_contrasts,
            separating_lower_metrics=diagnosis.separating_lower_metrics,
            separating_higher_metrics=diagnosis.separating_higher_metrics,
            classifier_labels=tuple(labels),
        )

    return diagnosis


def label_if_metric_strictly_lower(
    metric: str,
    *,
    label: str,
) -> Classifier:
    """Build a classifier that fires when ``metric`` cleanly separates low."""

    def _classify(diagnosis: SeedFailureDiagnosis) -> str | None:
        if metric in diagnosis.separating_lower_metrics:
            return label
        return None

    return _classify


def label_if_milestone_absent_on_hard(
    milestone: str,
    *,
    label: str,
    require_present_on_all_reference: bool = True,
) -> Classifier:
    """Build a classifier for milestones missing on every hard seed."""

    def _classify(diagnosis: SeedFailureDiagnosis) -> str | None:
        for contrast in diagnosis.milestone_contrasts:
            if contrast.milestone != milestone:
                continue
            if contrast.hard_present_count != 0:
                return None
            if require_present_on_all_reference and contrast.reference_present_count != len(
                diagnosis.reference_seeds
            ):
                return None
            return label
        return None

    return _classify


def profiles_from_metric_table(
    rows: Mapping[Any, Mapping[str, float | int | None]],
    *,
    outcomes: Mapping[Any, str | bool | None] | None = None,
    milestones: Mapping[Any, Mapping[str, int | None]] | None = None,
) -> tuple[SeedProfile, ...]:
    """Convenience builder from seed → metrics maps."""

    outcomes = outcomes or {}
    milestones = milestones or {}
    return tuple(
        SeedProfile(
            seed=seed,
            metrics=dict(metrics),
            milestones=dict(milestones.get(seed, {})),
            outcome=outcomes.get(seed),
        )
        for seed, metrics in rows.items()
    )
