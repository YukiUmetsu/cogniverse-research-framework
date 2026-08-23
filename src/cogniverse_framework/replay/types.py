"""Typed results for the generic replay/compare surface.

These types are framework infrastructure. Experiment-specific seeds, claim
strings, and timings belong in the learning lab (or injected adapter inputs).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class LaterLookup:
    """Result of searching for an item later in a peer sequence."""

    found: bool
    count: int
    indices: tuple[int, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "found": self.found,
            "count": self.count,
            "indices": list(self.indices),
        }


@dataclass(frozen=True)
class FirstDivergence:
    """First index where two sequences disagree."""

    index: int
    type: str = "value_difference"
    left: Any = None
    right: Any = None

    def to_dict(self) -> dict[str, Any]:
        payload = {"index": self.index, "type": self.type}
        if self.type != "length_difference":
            payload["left"] = self.left
            payload["right"] = self.right
        return payload


@dataclass(frozen=True)
class DivergencePoint:
    """Enriched first-divergence detail for an audit."""

    index: int
    type: str
    left: Any = None
    right: Any = None
    classification: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "type": self.type,
            "left": self.left,
            "right": self.right,
            "classification": self.classification,
        }


@dataclass(frozen=True)
class DivergenceResult:
    """Replay-only audit of how two event sequences diverge."""

    identical: bool
    shared_length: int
    divergence: DivergencePoint | None = None
    left_divergent_later_in_right: LaterLookup = field(
        default_factory=lambda: LaterLookup(False, 0, ())
    )
    right_divergent_later_in_left: LaterLookup = field(
        default_factory=lambda: LaterLookup(False, 0, ())
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "identical": self.identical,
            "shared_length": self.shared_length,
            "divergence": (
                None if self.divergence is None else self.divergence.to_dict()
            ),
            "left_divergent_later_in_right": (
                self.left_divergent_later_in_right.to_dict()
            ),
            "right_divergent_later_in_left": (
                self.right_divergent_later_in_left.to_dict()
            ),
        }


@dataclass(frozen=True)
class SharedAncestryResult:
    """Longest shared prefix between two ancestry sequences."""

    shared_length: int
    shared_states: tuple[Any, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "shared_length": self.shared_length,
            "shared_states": list(self.shared_states),
        }


@dataclass(frozen=True)
class SeedRow:
    """One seed's baseline vs candidate value."""

    seed: Any
    baseline: Any
    candidate: Any
    changed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SeedMatrixResult:
    """Side-by-side comparison of seed → value maps."""

    rows: tuple[SeedRow, ...] = ()

    @property
    def changed_seeds(self) -> list[Any]:
        return [row.seed for row in self.rows if row.changed]

    @property
    def changed_count(self) -> int:
        return len(self.changed_seeds)

    @property
    def baseline_count(self) -> int:
        return sum(1 for row in self.rows if row.baseline is not None)

    @property
    def candidate_count(self) -> int:
        return sum(1 for row in self.rows if row.candidate is not None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows": [row.to_dict() for row in self.rows],
            "changed_seeds": self.changed_seeds,
            "changed_count": self.changed_count,
            "baseline_count": self.baseline_count,
            "candidate_count": self.candidate_count,
        }


@dataclass(frozen=True)
class RunCompareResult:
    """Field-level diff of two run/result mappings."""

    changed: bool
    changed_fields: tuple[Any, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "changed": self.changed,
            "changed_fields": list(self.changed_fields),
        }


EMPTY_LATER = LaterLookup(found=False, count=0, indices=())
