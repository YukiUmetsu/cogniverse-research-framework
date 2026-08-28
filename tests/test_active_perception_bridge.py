import hashlib
import unittest

from cogniverse_framework.cognition import (
    ActivationPolicy,
    ActivePerceptionConsumer,
    CognitiveState,
    EdgeRelation,
    MemoryKind,
    NodeCategory,
    PerceptModality,
    PublicPercept,
    ReferenceKind,
)


def policy(**overrides) -> ActivationPolicy:
    values = dict(
        policy_id="bridge-policy",
        decay_ppm=900_000,
        perception_boost_ppm=500_000,
        spreading_boost_ppm=150_000,
        working_threshold_ppm=300_000,
        primed_threshold_ppm=100_000,
    )
    values.update(overrides)
    return ActivationPolicy(**values)


def percept(
    percept_id: str,
    *,
    logical_step: int = 1,
    evidence_ids: tuple[str, ...] = ("event-1",),
) -> PublicPercept:
    payload = f"{percept_id}:{logical_step}".encode("utf-8")
    return PublicPercept(
        percept_id=percept_id,
        modality=PerceptModality.STRUCTURED,
        source_system="fixture-perception",
        logical_step=logical_step,
        content_sha256=hashlib.sha256(payload).hexdigest(),
        confidence_ppm=750_000,
        evidence_ids=evidence_ids,
    )


class ActivePerceptionConsumerTests(unittest.TestCase):
    def test_receive_maps_percept_to_active_node_and_cognitive_state(self) -> None:
        consumer = ActivePerceptionConsumer(policy(), working_capacity=2)
        item = percept("entity-a", logical_step=3)
        result = consumer.receive(item)

        self.assertEqual(result.node.node_id, "percept.entity-a")
        self.assertEqual(result.node.category, NodeCategory.ENTITY)
        self.assertEqual(result.node.external_ref_id, "entity-a")
        self.assertEqual(result.cognitive_state.logical_step, 3)
        self.assertEqual(result.cognitive_state.state_id, "state-000003")
        self.assertTrue(result.cognitive_state.memories)
        self.assertTrue(
            all(memory.memory_kind is MemoryKind.EPISODIC for memory in result.cognitive_state.memories)
        )

    def test_pipeline_is_deterministic_for_ordered_percepts(self) -> None:
        sequence = (
            percept("entity-a", logical_step=1),
            percept("entity-b", logical_step=2),
        )
        first = ActivePerceptionConsumer.process_percepts(
            sequence,
            policy(),
            working_capacity=2,
        )
        second = ActivePerceptionConsumer.process_percepts(
            sequence,
            policy(),
            working_capacity=2,
        )
        self.assertEqual(
            first.cognitive_state.digest(),
            second.cognitive_state.digest(),
        )
        self.assertEqual(first.snapshot.digest(), second.snapshot.digest())

    def test_linking_percepts_enables_associative_spread(self) -> None:
        consumer = ActivePerceptionConsumer(policy(), working_capacity=2)
        left = percept("entity-a", logical_step=1)
        right = percept("entity-b", logical_step=1)
        consumer.receive(left)
        consumer.receive(right)
        consumer.link_percepts(left, right, relation=EdgeRelation.ASSOCIATED_WITH)

        neighbor = consumer.runtime.graph.get_node("percept.entity-b")
        self.assertIsNotNone(neighbor)
        assert neighbor is not None
        self.assertGreaterEqual(neighbor.activation_ppm, 150_000)

    def test_advance_decays_activation_without_new_percepts(self) -> None:
        consumer = ActivePerceptionConsumer(policy(), working_capacity=2)
        item = percept("entity-a", logical_step=1)
        before = consumer.receive(item).node.activation_ppm
        consumer.advance(2)
        node = consumer.runtime.graph.get_node("percept.entity-a")
        assert node is not None
        self.assertLess(node.activation_ppm, before)

    def test_custom_node_id_mapping_is_injected_not_hardcoded(self) -> None:
        consumer = ActivePerceptionConsumer(
            policy(),
            working_capacity=2,
            node_id_from_percept=lambda item: f"node.{item.percept_id}",
        )
        result = consumer.receive(percept("entity-a", logical_step=1))
        self.assertEqual(result.node.node_id, "node.entity-a")

    def test_projected_state_remains_cognitive_state_v1(self) -> None:
        result = ActivePerceptionConsumer.process_percepts(
            (percept("entity-a", logical_step=4),),
            policy(),
            working_capacity=2,
        )
        state = result.cognitive_state
        self.assertIsInstance(state, CognitiveState)
        self.assertEqual(state.to_dict()["schema_version"], "cognitive_state.v1")
        self.assertTrue(
            all(item.kind is ReferenceKind.MEMORY for item in state.memories)
        )

    def test_rejects_link_before_receive(self) -> None:
        consumer = ActivePerceptionConsumer(policy(), working_capacity=2)
        left = percept("entity-a", logical_step=1)
        right = percept("entity-b", logical_step=1)
        consumer.receive(left)
        with self.assertRaisesRegex(ValueError, "target percept must be received"):
            consumer.link_percepts(left, right)


if __name__ == "__main__":
    unittest.main()
