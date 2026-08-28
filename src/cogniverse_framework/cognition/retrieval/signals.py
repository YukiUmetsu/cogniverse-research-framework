"""Retrieval ranking signal types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar

from .._validation import validate_ppm


class RetrievalSignal(str, Enum):
    """Configurable ranking signals used by the reference retrieval controller."""

    GOAL_RELEVANCE = "goal_relevance"
    ASSOCIATIVE_RELEVANCE = "associative_relevance"
    TEMPORAL_RELEVANCE = "temporal_relevance"
    CAUSAL_RELEVANCE = "causal_relevance"
    SALIENCE = "salience"
    PREDICTION_USEFULNESS = "prediction_usefulness"
    RETRIEVAL_COST = "retrieval_cost"
    GAP_URGENCY = "gap_urgency"


@dataclass(frozen=True, slots=True)
class RetrievalScoreComponent:
    """One transparent contribution to a candidate score."""

    SCHEMA_VERSION: ClassVar[str] = "retrieval_score_component.v1"

    signal: RetrievalSignal
    weight_ppm: int
    value_ppm: int

    def __post_init__(self) -> None:
        validate_ppm("weight_ppm", self.weight_ppm)
        validate_ppm("value_ppm", self.value_ppm)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "signal": self.signal.value,
            "weight_ppm": self.weight_ppm,
            "value_ppm": self.value_ppm,
        }
