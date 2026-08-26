"""Shared validation helpers for typed cognitive contracts."""

from __future__ import annotations

import re


_FORBIDDEN_IDENTIFIER_TOKENS = frozenset(
    {"answer", "evaluator", "future", "hidden", "private"}
)


def validate_identifier(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{name} must be a non-empty trimmed string")
    tokens = set(filter(None, re.split(r"[^a-z0-9]+", value.lower())))
    forbidden = sorted(tokens & _FORBIDDEN_IDENTIFIER_TOKENS)
    if forbidden:
        raise ValueError(f"{name} contains forbidden marker: {forbidden[0]}")


def normalize_identifiers(name: str, values: tuple[str, ...]) -> tuple[str, ...]:
    normalized = tuple(values)
    for value in normalized:
        validate_identifier(name, value)
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{name} must contain unique identifiers")
    return tuple(sorted(normalized))


def validate_ppm(name: str, value: int | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 1_000_000:
        raise ValueError(f"{name} must be None or an integer from 0 to 1000000")
