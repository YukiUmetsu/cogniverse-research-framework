"""Activation policy and trace records for deterministic active cognition."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar

from .._validation import validate_identifier, validate_ppm
from .graph import clamp_activation_ppm


class ActivationSource(str, Enum):
    """Typed origin of an activation change."""

    PERCEPTION = "perception"
    DECAY = "decay"
    SPREADING = "spreading"
    GOAL_RELEVANCE = "goal_relevance"
    SALIENCE = "salience"
    RETRIEVAL = "retrieval"
    THRESHOLD = "threshold"
    CAPACITY = "capacity"


class ActivationReason(str, Enum):
    """Machine-readable reason codes for admission, eviction, and boosts."""

    PERCEPT_RECEIVED = "percept_received"
    ASSOCIATIVE_SPREAD = "associative_spread"
    LOGICAL_TICK_DECAY = "logical_tick_decay"
    WORKING_THRESHOLD_MET = "working_threshold_met"
    CAPACITY_EVICTION = "capacity_eviction"
    PRIMED_THRESHOLD_MET = "primed_threshold_met"
    BELOW_PRIMED_THRESHOLD = "below_primed_threshold"
    BELOW_WORKING_THRESHOLD = "below_working_threshold"
    MEMORY_RETRIEVED = "memory_retrieved"


@dataclass(frozen=True, slots=True)
class ActivationPolicy:
    """Injected weights and thresholds; the framework does not hide experiment policy."""

    SCHEMA_VERSION: ClassVar[str] = "activation_policy.v1"

    policy_id: str
    decay_ppm: int
    perception_boost_ppm: int
    spreading_boost_ppm: int
    working_threshold_ppm: int
    primed_threshold_ppm: int
    goal_relevance_boost_ppm: int = 0
    salience_boost_ppm: int = 0
    retrieval_boost_ppm: int = 0

    def __post_init__(self) -> None:
        validate_identifier("policy_id", self.policy_id)
        for field_name in (
            "decay_ppm",
            "perception_boost_ppm",
            "spreading_boost_ppm",
            "working_threshold_ppm",
            "primed_threshold_ppm",
            "goal_relevance_boost_ppm",
            "salience_boost_ppm",
            "retrieval_boost_ppm",
        ):
            validate_ppm(field_name, getattr(self, field_name))
        if self.primed_threshold_ppm > self.working_threshold_ppm:
            raise ValueError("primed_threshold_ppm must be <= working_threshold_ppm")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "policy_id": self.policy_id,
            "decay_ppm": self.decay_ppm,
            "perception_boost_ppm": self.perception_boost_ppm,
            "spreading_boost_ppm": self.spreading_boost_ppm,
            "working_threshold_ppm": self.working_threshold_ppm,
            "primed_threshold_ppm": self.primed_threshold_ppm,
            "goal_relevance_boost_ppm": self.goal_relevance_boost_ppm,
            "salience_boost_ppm": self.salience_boost_ppm,
            "retrieval_boost_ppm": self.retrieval_boost_ppm,
        }


@dataclass(frozen=True, slots=True)
class ActivationRecord:
    """One inspectable activation transition for replay and audit."""

    SCHEMA_VERSION: ClassVar[str] = "activation_record.v1"

    record_id: str
    node_id: str
    logical_step: int
    previous_activation_ppm: int
    new_activation_ppm: int
    source: ActivationSource
    reason: ActivationReason

    def __post_init__(self) -> None:
        validate_identifier("record_id", self.record_id)
        validate_identifier("node_id", self.node_id)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        validate_ppm("previous_activation_ppm", self.previous_activation_ppm)
        validate_ppm("new_activation_ppm", self.new_activation_ppm)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "record_id": self.record_id,
            "node_id": self.node_id,
            "logical_step": self.logical_step,
            "previous_activation_ppm": self.previous_activation_ppm,
            "new_activation_ppm": self.new_activation_ppm,
            "source": self.source.value,
            "reason": self.reason.value,
        }


def apply_decay(activation_ppm: int, *, decay_ppm: int) -> int:
    """Decay activation by a configured retention factor."""

    validate_ppm("decay_ppm", decay_ppm)
    validate_ppm("activation_ppm", activation_ppm)
    return clamp_activation_ppm((activation_ppm * decay_ppm) // 1_000_000)


def apply_boost(activation_ppm: int, *, boost_ppm: int) -> int:
    """Add a configured boost without exceeding the ppm range."""

    validate_ppm("activation_ppm", activation_ppm)
    validate_ppm("boost_ppm", boost_ppm)
    return clamp_activation_ppm(activation_ppm + boost_ppm)
