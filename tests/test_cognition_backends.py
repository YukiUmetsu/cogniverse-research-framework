import hashlib
import unittest
from unittest import mock

from cogniverse_framework.cognition import (
    ActivationPolicy,
    ActiveCognitionCoordinator,
    CognitiveEventKind,
    InMemoryEventBus,
    InMemoryMemoryStoreSet,
    NodeCategory,
    PerceptModality,
    PublicPercept,
    RetrievalRankingPolicy,
    create_event_bus,
    create_memory_store_set,
    episodic_memory_record,
)


def digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def activation_policy(**overrides) -> ActivationPolicy:
    values = dict(
        policy_id="backend-test-activation",
        decay_ppm=900_000,
        perception_boost_ppm=500_000,
        spreading_boost_ppm=100_000,
        working_threshold_ppm=300_000,
        primed_threshold_ppm=100_000,
        retrieval_boost_ppm=200_000,
    )
    values.update(overrides)
    return ActivationPolicy(**values)


def ranking_policy(**overrides) -> RetrievalRankingPolicy:
    values = dict(
        policy_id="backend-test-ranking",
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
    values.update(overrides)
    return RetrievalRankingPolicy(**values)


def event_percept(logical_step: int = 1) -> PublicPercept:
    return PublicPercept(
        percept_id="event-1",
        modality=PerceptModality.STRUCTURED,
        source_system="fixture-perception",
        logical_step=logical_step,
        content_sha256=digest(f"event-1:{logical_step}"),
        evidence_ids=("event-1",),
    )


class BackendFactoryTests(unittest.TestCase):
    def test_create_inmemory_backends(self) -> None:
        memory = create_memory_store_set("inmemory")
        bus = create_event_bus("inmemory")
        self.assertIsInstance(memory, InMemoryMemoryStoreSet)
        self.assertIsInstance(bus, InMemoryEventBus)

    def test_create_redis_backends_requires_package(self) -> None:
        with mock.patch(
            "cogniverse_framework.cognition.backends.redis_backend._require_redis",
            side_effect=ImportError("redis not installed"),
        ):
            with self.assertRaises(ImportError):
                create_memory_store_set("redis")


class ActiveCognitionCoordinatorTests(unittest.TestCase):
    def test_receive_and_retrieve_publishes_events_and_materializes_memory(self) -> None:
        coordinator = ActiveCognitionCoordinator(
            activation_policy(),
            ranking_policy(),
            working_capacity=4,
            memory_stores=InMemoryMemoryStoreSet(),
            event_bus=InMemoryEventBus(),
            node_category=NodeCategory.EVENT,
        )
        coordinator.store_memory(
            episodic_memory_record(
                memory_id="episode-1",
                source_system="fixture-memory",
                logical_step=1,
                content_sha256=digest("episode-1"),
                evidence_ids=("evidence-1",),
                related_node_ids=("percept.event-1",),
            )
        )

        result = coordinator.receive_and_retrieve(
            event_percept(),
            goal_node_ids=("percept.event-1",),
        )

        self.assertIsNotNone(result.cognitive_state)
        self.assertTrue(result.retrieval is not None and result.retrieval.gaps)
        self.assertTrue(any(event.kind is CognitiveEventKind.PERCEPT_RECEIVED for event in result.events_published))
        self.assertTrue(any(event.kind is CognitiveEventKind.MEMORY_RETRIEVED for event in result.events_published))
        self.assertIsNotNone(coordinator.runtime.graph.get_node("memory.episode-1"))
        self.assertGreaterEqual(
            coordinator.activation_store.latest_activation(node_id="memory.episode-1")[1],
            0,
        )

    def test_event_bus_replay_is_deterministic(self) -> None:
        bus = InMemoryEventBus()
        coordinator = ActiveCognitionCoordinator(
            activation_policy(),
            ranking_policy(),
            working_capacity=2,
            event_bus=bus,
        )
        coordinator.receive_percept(event_percept())
        first = bus.replay()
        second = bus.replay()
        self.assertEqual(tuple(item.digest() for item in first), tuple(item.digest() for item in second))


if __name__ == "__main__":
    unittest.main()
