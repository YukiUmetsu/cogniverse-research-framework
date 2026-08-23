"""Seed-matrix mutation comparison.

Thin wrapper over ``replay.compare.compare_seed_matrix``. Prefer the replay
compare API directly for new code.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cogniverse_framework.replay.compare import compare_seed_matrix
from cogniverse_framework.replay.types import SeedMatrixResult


@dataclass
class MutationAnalysis:
    """Compare baseline vs candidate seed → value maps."""

    baseline: Mapping[Any, Any]
    candidate: Mapping[Any, Any]

    def compare(self) -> SeedMatrixResult:
        return compare_seed_matrix(self.baseline, self.candidate)
