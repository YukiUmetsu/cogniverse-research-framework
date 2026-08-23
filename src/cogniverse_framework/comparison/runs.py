"""Field-level comparison of run/result mappings."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from cogniverse_framework.replay.compare import compare_runs as _compare_runs


def compare_runs(
    left: Mapping[Any, Any],
    right: Mapping[Any, Any],
) -> dict[str, Any]:
    """Return a dict-shaped field diff for legacy callers."""

    return _compare_runs(left, right).to_dict()
