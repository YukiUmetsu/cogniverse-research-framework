"""Replay-only sequence divergence helpers.

Generic infrastructure: callers supply sequences and classifiers. No
environment execution and no experiment-specific science.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from .types import (
    EMPTY_LATER,
    DivergencePoint,
    DivergenceResult,
    FirstDivergence,
    LaterLookup,
)


def first_divergence(
    left: Sequence[Any],
    right: Sequence[Any],
) -> FirstDivergence | None:
    length = min(len(left), len(right))

    for i in range(length):
        if left[i] != right[i]:
            return FirstDivergence(
                index=i,
                type="value_difference",
                left=left[i],
                right=right[i],
            )

    if len(left) != len(right):
        return FirstDivergence(index=length, type="length_difference")

    return None


def classify_transition_divergence(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    *,
    state_key: str = "before_state_id",
    action_key: str = "action_id",
    outcome_key: str = "after_state_id",
) -> str:
    """Classify how two transition-like events diverge.

    Returns one of:
    - different_frontier_state
    - different_action_same_state
    - different_outcome_same_state_action
    - identical
    """

    if dict(left) == dict(right):
        return "identical"

    if left.get(state_key) != right.get(state_key):
        return "different_frontier_state"

    if left.get(action_key) != right.get(action_key):
        return "different_action_same_state"

    if left.get(outcome_key) != right.get(outcome_key):
        return "different_outcome_same_state_action"

    return "identical"


def find_later(
    sequence: Sequence[Any],
    item: Any,
    *,
    start: int = 0,
    key: Callable[[Any], Any] | None = None,
) -> LaterLookup:
    """Locate later occurrences of item in sequence[start:]."""

    identity = key or (lambda value: value)
    target = identity(item)
    indices = tuple(
        index
        for index, value in enumerate(sequence[start:], start=start)
        if identity(value) == target
    )
    return LaterLookup(
        found=bool(indices),
        count=len(indices),
        indices=indices,
    )


def audit_sequence_divergence(
    left: Sequence[Any],
    right: Sequence[Any],
    *,
    identity: Callable[[Any], Any] | None = None,
    classify: Callable[[Any, Any], str] | None = None,
) -> DivergenceResult:
    """Replay-only audit of the first sequence divergence."""

    key = identity or (lambda value: value)
    left_keys = [key(item) for item in left]
    right_keys = [key(item) for item in right]
    divergence = first_divergence(left_keys, right_keys)

    if divergence is None:
        return DivergenceResult(
            identical=True,
            shared_length=len(left_keys),
            divergence=None,
            left_divergent_later_in_right=EMPTY_LATER,
            right_divergent_later_in_left=EMPTY_LATER,
        )

    index = divergence.index
    left_event = left[index] if index < len(left) else None
    right_event = right[index] if index < len(right) else None

    classification = None
    if (
        classify is not None
        and left_event is not None
        and right_event is not None
        and divergence.type != "length_difference"
    ):
        classification = classify(left_event, right_event)

    left_later = (
        find_later(right, left_event, start=index, key=key)
        if left_event is not None
        else EMPTY_LATER
    )
    right_later = (
        find_later(left, right_event, start=index, key=key)
        if right_event is not None
        else EMPTY_LATER
    )

    return DivergenceResult(
        identical=False,
        shared_length=index,
        divergence=DivergencePoint(
            index=index,
            type=divergence.type,
            left=left_event,
            right=right_event,
            classification=classification,
        ),
        left_divergent_later_in_right=left_later,
        right_divergent_later_in_left=right_later,
    )


def post_divergence_budget(
    events: Sequence[Mapping[str, Any]],
    start_index: int,
    *,
    category_getters: Mapping[str, Callable[[Mapping[str, Any]], str]],
) -> dict[str, dict[str, int]]:
    """Count labeled budget spend for events at and after start_index."""

    totals: dict[str, Counter[str]] = {
        name: Counter() for name in category_getters
    }

    for event in events[start_index:]:
        for name, getter in category_getters.items():
            totals[name][getter(event)] += 1

    return {
        name: dict(counter)
        for name, counter in totals.items()
    }
