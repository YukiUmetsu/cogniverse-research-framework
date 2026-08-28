"""Reference fixture for Learning Lab coordinator wiring.

Copy this pattern into the Learning Lab after pinning the framework commit.
The framework cannot import the lab; this test documents the expected wiring.
"""

from __future__ import annotations

import hashlib
import unittest

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
from cogniverse_framework.replay import build_event_trace, event_trace_to_evidence_payload


def digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def lab_activation_policy() -> ActivationPolicy:
    """Lab injects thresholds from experiment configuration — not framework defaults."""
    return ActivationPolicy(
        policy_id="lab-fixture-activation",
        decay_ppm=900_000,
        perception_boost_ppm=500_000,
        spreading_boost_ppm=100_000,
        working_threshold_ppm=300_000,
        primed_threshold_ppm=100_000,
        retrieval_boost_ppm=200_000,
    )


def lab_ranking_policy() -> RetrievalRankingPolicy:
    return RetrievalRankingPolicy(
        policy_id="lab-fixture-ranking",
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


def lab_environment_to_public_percept(logical_step: int = 1) -> PublicPercept:
    """Thin adapter: environment observation → PublicPercept (implement in lab)."""
    return PublicPercept(
        percept_id="event-1",
        modality=PerceptModality.STRUCTURED,
        source_system="lab-environment-adapter",
        logical_step=logical_step,
        content_sha256=digest(f"event-1:{logical_step}"),
        evidence_ids=("event-1",),
    )


def build_lab_coordinator() -> ActiveCognitionCoordinator:
    coordinator = ActiveCognitionCoordinator(
        lab_activation_policy(),
        lab_ranking_policy(),
        working_capacity=4,
        memory_backend="inmemory",
        event_backend="inmemory",
        node_category=NodeCategory.EVENT,
        source_system="lab-active-cognition-consumer",
    )
    coordinator.store_memory(
        episodic_memory_record(
            memory_id="episode-1",
            source_system="lab-memory",
            logical_step=1,
            content_sha256=digest("episode-1"),
            evidence_ids=("evidence-1",),
            related_node_ids=("percept.event-1",),
        )
    )
    return coordinator


class CoordinatorReferenceFixtureTests(unittest.TestCase):
    def test_lab_consumer_wiring_produces_auditable_state_and_events(self) -> None:
        coordinator = build_lab_coordinator()
        result = coordinator.receive_and_retrieve(
            lab_environment_to_public_percept(),
            goal_node_ids=("percept.event-1",),
        )

        self.assertIsNotNone(result.cognitive_state)
        self.assertIsNotNone(result.snapshot)
        self.assertTrue(result.retrieval is not None and result.retrieval.gaps)
        self.assertTrue(
            any(event.kind is CognitiveEventKind.PERCEPT_RECEIVED for event in result.events_published)
        )
        self.assertTrue(
            any(event.kind is CognitiveEventKind.MEMORY_RETRIEVED for event in result.events_published)
        )

        trace = build_event_trace(
            coordinator.replay_events(),
            source_system="lab-active-cognition-consumer",
        )
        evidence_payload = event_trace_to_evidence_payload(trace)
        self.assertEqual(evidence_payload["artifact_kind"], "cognitive_event_trace")
        self.assertEqual(evidence_payload["trace_digest"], trace.digest())
        self.assertIsNotNone(result.snapshot.digest())
        self.assertIsNotNone(result.cognitive_state.digest())

    def test_deterministic_replay_for_equivalence_checks(self) -> None:
        first = build_lab_coordinator()
        second = build_lab_coordinator()
        percept = lab_environment_to_public_percept()

        first_result = first.receive_and_retrieve(percept, goal_node_ids=("percept.event-1",))
        second_result = second.receive_and_retrieve(percept, goal_node_ids=("percept.event-1",))

        self.assertEqual(first_result.to_dict(), second_result.to_dict())
        first_trace = build_event_trace(first.replay_events(), source_system="lab-active-cognition-consumer")
        second_trace = build_event_trace(second.replay_events(), source_system="lab-active-cognition-consumer")
        self.assertEqual(first_trace.digest(), second_trace.digest())


if __name__ == "__main__":
    unittest.main()
