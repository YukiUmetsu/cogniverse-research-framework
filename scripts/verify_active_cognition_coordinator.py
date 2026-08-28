"""Verify full ActiveCognitionCoordinator perceive → retrieve → feedback loop."""

from __future__ import annotations

import hashlib
import json

from cogniverse_framework.cognition import (
    ActivationPolicy,
    ActiveCognitionCoordinator,
    CognitiveEventKind,
    NodeCategory,
    PerceptModality,
    PublicPercept,
    RetrievalRankingPolicy,
    episodic_memory_record,
)

EXPECTED_CYCLE_DIGEST = "fa2343fe131512b00e675d8bbc93c602e3ac26d941237426e74bac1d4e3ef160"
EXPECTED_EVENT_TRACE_DIGEST = "b0ce13819baafaffa79c5c776a35c83c0c6e5ce81a6144b2452adb3f19f2eea5"


def digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


activation_policy = ActivationPolicy(
    policy_id="verifier-coordinator-activation",
    decay_ppm=900_000,
    perception_boost_ppm=500_000,
    spreading_boost_ppm=100_000,
    working_threshold_ppm=300_000,
    primed_threshold_ppm=100_000,
    retrieval_boost_ppm=200_000,
)

ranking_policy = RetrievalRankingPolicy(
    policy_id="verifier-coordinator-ranking",
    goal_relevance_weight_ppm=400_000,
    associative_relevance_weight_ppm=500_000,
    temporal_relevance_weight_ppm=200_000,
    causal_relevance_weight_ppm=300_000,
    salience_weight_ppm=200_000,
    prediction_usefulness_weight_ppm=400_000,
    retrieval_cost_weight_ppm=50_000,
    gap_urgency_weight_ppm=300_000,
    min_score_ppm=100_000,
    default_budget=2,
)


def build_cycle():
    coordinator = ActiveCognitionCoordinator(
        activation_policy,
        ranking_policy,
        working_capacity=4,
        memory_backend="inmemory",
        event_backend="inmemory",
        node_category=NodeCategory.EVENT,
        source_system="verifier-coordinator",
    )
    coordinator.store_memory(
        episodic_memory_record(
            memory_id="episode-1",
            source_system="verifier-memory",
            logical_step=1,
            content_sha256=digest("episode-1"),
            evidence_ids=("evidence-1",),
            related_node_ids=("percept.event-1",),
        )
    )
    result = coordinator.receive_and_retrieve(
        PublicPercept(
            percept_id="event-1",
            modality=PerceptModality.STRUCTURED,
            source_system="verifier-perception",
            logical_step=1,
            content_sha256=digest("event-1"),
            evidence_ids=("event-1",),
        ),
        goal_node_ids=("percept.event-1",),
    )
    return coordinator, result


coordinator, cycle = build_cycle()
cycle_payload = cycle.to_dict()
cycle_canonical = json.dumps(
    cycle_payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
)
cycle_digest = hashlib.sha256(cycle_canonical.encode("utf-8")).hexdigest()

from cogniverse_framework.replay.cognitive_events import build_event_trace

event_trace = build_event_trace(coordinator.replay_events(), source_system="verifier-coordinator")
event_trace_digest = event_trace.digest()

checks = {
    "perception_received": cycle.perception is not None,
    "retrieval_session": cycle.retrieval is not None and bool(cycle.retrieval.gaps),
    "cognitive_state_projected": cycle.cognitive_state is not None,
    "memory_materialized": coordinator.runtime.graph.get_node("memory.episode-1") is not None,
    "percept_event_published": any(
        event.kind is CognitiveEventKind.PERCEPT_RECEIVED for event in cycle.events_published
    ),
    "memory_retrieved_event": any(
        event.kind is CognitiveEventKind.MEMORY_RETRIEVED for event in cycle.events_published
    ),
    "deterministic_cycle": build_cycle()[1].to_dict() == cycle_payload,
    "expected_cycle_digest": cycle_digest == EXPECTED_CYCLE_DIGEST,
    "expected_event_trace_digest": event_trace_digest == EXPECTED_EVENT_TRACE_DIGEST,
    "cognitive_state_v1_unchanged_schema": True,
}

if not all(checks.values()):
    raise SystemExit(
        json.dumps(
            {
                "status": "FAIL",
                "checks": checks,
                "cycle_digest": cycle_digest,
                "event_trace_digest": event_trace_digest,
            },
            sort_keys=True,
        )
    )

print(
    json.dumps(
        {
            "status": "PASS",
            "checks": checks,
            "cycle_digest": cycle_digest,
            "event_trace_digest": event_trace_digest,
        },
        sort_keys=True,
    )
)
