"""Ancestry helpers for replay graphs.

Generic infrastructure for first-reach parent maps and shared prefixes.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .types import SharedAncestryResult


def shared_ancestry(
    left: Sequence[Any],
    right: Sequence[Any],
) -> SharedAncestryResult:
    shared: list[Any] = []

    for a, b in zip(left, right):
        if a != b:
            break
        shared.append(a)

    return SharedAncestryResult(
        shared_length=len(shared),
        shared_states=tuple(shared),
    )


def first_reach_parents(
    edges: Sequence[tuple[Any, Any]],
    *,
    root: Any | None = None,
) -> dict[Any, Any | None]:
    """Build first-reach parent map from ordered (before, after) edges."""

    parents: dict[Any, Any | None] = {}
    if root is not None:
        parents[root] = None

    for before, after in edges:
        if before not in parents:
            parents[before] = None
        if after not in parents:
            parents[after] = before

    return parents


def ancestry_path(
    parents: dict[Any, Any | None],
    target: Any,
) -> list[Any]:
    """Return root→target path using first-reach parents."""

    if target not in parents:
        return []

    reversed_path: list[Any] = []
    seen: set[Any] = set()
    current: Any | None = target

    while current is not None and current not in seen:
        seen.add(current)
        reversed_path.append(current)
        current = parents.get(current)

    reversed_path.reverse()
    return reversed_path
