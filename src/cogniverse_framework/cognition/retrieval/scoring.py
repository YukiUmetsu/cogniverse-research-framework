"""Transparent retrieval ranking policy and scoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

from .._validation import validate_identifier, validate_ppm
from ..state import MemoryKind
from .gaps import GapKind
from .records import LongTermMemoryRecord
from .requests import RetrievalCandidate, RetrievalRequest
from .signals import RetrievalScoreComponent, RetrievalSignal


def clamp_score_ppm(value: int) -> int:
    return max(0, min(1_000_000, value))


@dataclass(frozen=True, slots=True)
class RetrievalRankingPolicy:
    """Injected weights and thresholds for deterministic candidate ranking."""

    SCHEMA_VERSION: ClassVar[str] = "retrieval_ranking_policy.v1"

    policy_id: str
    goal_relevance_weight_ppm: int
    associative_relevance_weight_ppm: int
    temporal_relevance_weight_ppm: int
    causal_relevance_weight_ppm: int
    salience_weight_ppm: int
    prediction_usefulness_weight_ppm: int
    retrieval_cost_weight_ppm: int
    gap_urgency_weight_ppm: int
    min_score_ppm: int
    default_budget: int

    def __post_init__(self) -> None:
        validate_identifier("policy_id", self.policy_id)
        for field_name in (
            "goal_relevance_weight_ppm",
            "associative_relevance_weight_ppm",
            "temporal_relevance_weight_ppm",
            "causal_relevance_weight_ppm",
            "salience_weight_ppm",
            "prediction_usefulness_weight_ppm",
            "retrieval_cost_weight_ppm",
            "gap_urgency_weight_ppm",
            "min_score_ppm",
        ):
            validate_ppm(field_name, getattr(self, field_name))
        if (
            isinstance(self.default_budget, bool)
            or not isinstance(self.default_budget, int)
            or self.default_budget < 1
        ):
            raise ValueError("default_budget must be a positive integer")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "policy_id": self.policy_id,
            "goal_relevance_weight_ppm": self.goal_relevance_weight_ppm,
            "associative_relevance_weight_ppm": self.associative_relevance_weight_ppm,
            "temporal_relevance_weight_ppm": self.temporal_relevance_weight_ppm,
            "causal_relevance_weight_ppm": self.causal_relevance_weight_ppm,
            "salience_weight_ppm": self.salience_weight_ppm,
            "prediction_usefulness_weight_ppm": self.prediction_usefulness_weight_ppm,
            "retrieval_cost_weight_ppm": self.retrieval_cost_weight_ppm,
            "gap_urgency_weight_ppm": self.gap_urgency_weight_ppm,
            "min_score_ppm": self.min_score_ppm,
            "default_budget": self.default_budget,
        }


def _overlap_ppm(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    if not left or not right:
        return 0
    overlap = len(set(left) & set(right))
    denominator = max(len(set(left) | set(right)), 1)
    return clamp_score_ppm((overlap * 1_000_000) // denominator)


def _temporal_relevance_ppm(
    request_step: int,
    record_step: int,
    *,
    horizon: int = 32,
) -> int:
    distance = abs(request_step - record_step)
    if distance >= horizon:
        return 0
    return clamp_score_ppm(((horizon - distance) * 1_000_000) // horizon)


def _gap_kind_role_bias(gap_kind: GapKind, memory_kind: MemoryKind) -> int:
    if gap_kind is GapKind.UNKNOWN_CAUSE and memory_kind is MemoryKind.EPISODIC:
        return 900_000
    if gap_kind is GapKind.UNKNOWN_GOAL_PRECONDITION and memory_kind is MemoryKind.PROCEDURAL:
        return 900_000
    if gap_kind is GapKind.UNRESOLVED_BELIEF_CONFLICT and memory_kind is MemoryKind.SEMANTIC:
        return 900_000
    if gap_kind is GapKind.LOW_PREDICTION_CONFIDENCE and memory_kind is MemoryKind.SEMANTIC:
        return 700_000
    return 300_000


def score_memory_record(
    request: RetrievalRequest,
    record: LongTermMemoryRecord,
    policy: RetrievalRankingPolicy,
) -> RetrievalCandidate | None:
    """Rank one memory record against a retrieval request."""

    if record.memory_kind not in request.memory_roles:
        return None

    context_nodes = (
        request.goal_node_ids
        + request.primed_node_ids
        + request.working_node_ids
        + (request.gap.subject_node_id,)
    )
    associative = _overlap_ppm(record.related_node_ids, context_nodes)
    goal = _overlap_ppm(record.related_node_ids, request.goal_node_ids)
    temporal = _temporal_relevance_ppm(request.logical_step, record.logical_step)
    causal = associative if request.gap.kind is GapKind.UNKNOWN_CAUSE else 0
    salience = _overlap_ppm(record.related_node_ids, request.working_node_ids)
    prediction = _gap_kind_role_bias(request.gap.kind, record.memory_kind)
    retrieval_cost = 100_000
    gap_urgency = request.gap.urgency_ppm if request.gap.urgency_ppm is not None else 500_000

    components = (
        RetrievalScoreComponent(
            RetrievalSignal.GOAL_RELEVANCE,
            policy.goal_relevance_weight_ppm,
            goal,
        ),
        RetrievalScoreComponent(
            RetrievalSignal.ASSOCIATIVE_RELEVANCE,
            policy.associative_relevance_weight_ppm,
            associative,
        ),
        RetrievalScoreComponent(
            RetrievalSignal.TEMPORAL_RELEVANCE,
            policy.temporal_relevance_weight_ppm,
            temporal,
        ),
        RetrievalScoreComponent(
            RetrievalSignal.CAUSAL_RELEVANCE,
            policy.causal_relevance_weight_ppm,
            causal,
        ),
        RetrievalScoreComponent(
            RetrievalSignal.SALIENCE,
            policy.salience_weight_ppm,
            salience,
        ),
        RetrievalScoreComponent(
            RetrievalSignal.PREDICTION_USEFULNESS,
            policy.prediction_usefulness_weight_ppm,
            prediction,
        ),
        RetrievalScoreComponent(
            RetrievalSignal.GAP_URGENCY,
            policy.gap_urgency_weight_ppm,
            gap_urgency,
        ),
        RetrievalScoreComponent(
            RetrievalSignal.RETRIEVAL_COST,
            policy.retrieval_cost_weight_ppm,
            retrieval_cost,
        ),
    )

    total = 0
    for component in components:
        contribution = (component.weight_ppm * component.value_ppm) // 1_000_000
        if component.signal is RetrievalSignal.RETRIEVAL_COST:
            total -= contribution
        else:
            total += contribution
    score = clamp_score_ppm(total)
    if score < policy.min_score_ppm:
        return None

    return RetrievalCandidate(
        memory_id=record.memory_id,
        memory_kind=record.memory_kind,
        score_ppm=score,
        score_components=components,
        evidence_ids=record.evidence_ids,
    )
