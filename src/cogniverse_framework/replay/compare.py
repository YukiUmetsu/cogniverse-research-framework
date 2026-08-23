"""Coherent replay/compare API for runs and seed matrices.

Folds the older parallel helpers (`comparison`, `seed_matrix`, research
`MutationAnalysis`) into one typed surface. Callers should prefer these
entry points over the thin compatibility shims.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .types import RunCompareResult, SeedMatrixResult, SeedRow


def _seed_sort_key(seed: Any) -> tuple[str, str]:
    """Sort seeds even when types differ (e.g. int vs str)."""

    return (type(seed).__name__, str(seed))


def compare_seed_matrix(
    baseline: Mapping[Any, Any],
    candidate: Mapping[Any, Any],
) -> SeedMatrixResult:
    """Compare seed → value maps (mutation timing, scores, etc.)."""

    seeds = sorted(set(baseline) | set(candidate), key=_seed_sort_key)
    rows = tuple(
        SeedRow(
            seed=seed,
            baseline=baseline.get(seed),
            candidate=candidate.get(seed),
            changed=baseline.get(seed) != candidate.get(seed),
        )
        for seed in seeds
    )
    return SeedMatrixResult(rows=rows)


def compare_runs(
    baseline: Any,
    candidate: Any,
) -> RunCompareResult:
    """Compare two run payloads.

    Mapping inputs yield a field-level diff. Non-mapping inputs fall back to
    equality (useful for opaque trajectory blobs).
    """

    if isinstance(baseline, Mapping) and isinstance(candidate, Mapping):
        keys = set(baseline) | set(candidate)
        changed_fields = tuple(
            sorted(
                (key for key in keys if baseline.get(key) != candidate.get(key)),
                key=_seed_sort_key,
            )
        )
        return RunCompareResult(
            changed=bool(changed_fields),
            changed_fields=changed_fields,
        )

    changed = baseline != candidate
    return RunCompareResult(
        changed=changed,
        changed_fields=("value",) if changed else (),
    )
