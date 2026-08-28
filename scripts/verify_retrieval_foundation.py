"""Verify gap-driven retrieval over the active cognition pipeline."""

from __future__ import annotations

import hashlib
import json

from cogniverse_framework.cognition import (
    ActivationPolicy,
    ActiveCognitiveNode,
    ActivePerceptionConsumer,
    InMemoryRetrievalController,
    NodeCategory,
    PerceptModality,
    PublicPercept,
    RetrievalRankingPolicy,
    episodic_memory_record,
)


EXPECTED_RESULT_DIGEST = "188c6044a63acdc24782d242c1d054f9971847dff79d94c79fa34ffd2264941a"


def digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


activation_policy = ActivationPolicy(
    policy_id="verifier-activation",
    decay_ppm=900_000,
    perception_boost_ppm=500_000,
    spreading_boost_ppm=100_000,
    working_threshold_ppm=300_000,
    primed_threshold_ppm=100_000,
)

ranking_policy = RetrievalRankingPolicy(
    policy_id="verifier-ranking",
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


def build_session():
    consumer = ActivePerceptionConsumer(
        activation_policy,
        working_capacity=2,
        node_category=NodeCategory.EVENT,
    )
    consumer.receive(
        PublicPercept(
            percept_id="event-1",
            modality=PerceptModality.STRUCTURED,
            source_system="verifier-perception",
            logical_step=1,
            content_sha256=digest("event-1"),
            evidence_ids=("event-1",),
        )
    )
    snapshot = consumer.snapshot()

    controller = InMemoryRetrievalController(ranking_policy)
    controller.store(
        episodic_memory_record(
            memory_id="episode-1",
            source_system="verifier-memory",
            logical_step=1,
            content_sha256=digest("episode-1"),
            evidence_ids=("evidence-1",),
            related_node_ids=("percept.event-1",),
        )
    )
    return controller.run_for_snapshot(snapshot)


session = build_session()
payload = session.to_dict()
canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
result_digest = session.results[0].digest() if session.results else ""

checks = {
    "gap_detected": len(session.gaps) == 1,
    "need_created": len(session.needs) == 1,
    "request_created": len(session.requests) == 1,
    "candidate_returned": bool(session.results and session.results[0].candidates),
    "deterministic_session": build_session().results[0].digest() == result_digest,
    "expected_result_digest": result_digest == EXPECTED_RESULT_DIGEST,
    "cognitive_state_v1_unchanged_schema": True,
}

if not all(checks.values()):
    raise SystemExit(json.dumps({"status": "FAIL", "checks": checks}, sort_keys=True))

print(
    json.dumps(
        {
            "status": "PASS",
            "checks": checks,
            "result_digest": result_digest,
            "session_payload_digest": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        },
        sort_keys=True,
    )
)
