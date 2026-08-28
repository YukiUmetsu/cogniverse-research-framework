import dataclasses
import json
import unittest

from cogniverse_framework.cognition import (
    ActivationPolicy,
    ActivationReason,
    ActivationSource,
    ActiveCognitiveEdge,
    ActiveCognitiveGraph,
    ActiveCognitiveNode,
    CognitiveState,
    EdgeRelation,
    InMemoryActiveCognitionRuntime,
    MemoryKind,
    NodeCategory,
    ReferenceKind,
)


def policy(**overrides) -> ActivationPolicy:
    values = dict(
        policy_id="test-policy",
        decay_ppm=900_000,
        perception_boost_ppm=500_000,
        spreading_boost_ppm=150_000,
        working_threshold_ppm=300_000,
        primed_threshold_ppm=100_000,
    )
    values.update(overrides)
    return ActivationPolicy(**values)


def node(
    node_id: str,
    *,
    logical_step: int = 1,
    activation_ppm: int = 0,
    evidence_ids: tuple[str, ...] = ("evidence-1",),
) -> ActiveCognitiveNode:
    return ActiveCognitiveNode(
        node_id=node_id,
        category=NodeCategory.ENTITY,
        source_system="perception",
        logical_step=logical_step,
        activation_ppm=activation_ppm,
        evidence_ids=evidence_ids,
    )


class ActiveCognitiveGraphTests(unittest.TestCase):
    def test_graph_serialization_is_deterministic(self) -> None:
        first = ActiveCognitiveGraph(
            logical_step=2,
            nodes=(
                node("node-b", logical_step=2),
                node("node-a", logical_step=2),
            ),
            edges=(
                ActiveCognitiveEdge(
                    edge_id="edge-b",
                    source_id="node-a",
                    target_id="node-b",
                    relation=EdgeRelation.ASSOCIATED_WITH,
                    source_system="perception",
                    logical_step=2,
                    evidence_ids=("evidence-1",),
                ),
                ActiveCognitiveEdge(
                    edge_id="edge-a",
                    source_id="node-a",
                    target_id="node-b",
                    relation=EdgeRelation.PREDICTS,
                    source_system="perception",
                    logical_step=2,
                    evidence_ids=("evidence-2",),
                ),
            ),
        )
        second = ActiveCognitiveGraph(
            logical_step=2,
            nodes=(node("node-a", logical_step=2), node("node-b", logical_step=2)),
            edges=first.edges[::-1],
        )
        self.assertEqual(first.canonical_json(), second.canonical_json())
        self.assertEqual(first.digest(), second.digest())

    def test_rejects_edge_without_endpoints(self) -> None:
        graph = ActiveCognitiveGraph(logical_step=1, nodes=(node("node-a"),))
        with self.assertRaisesRegex(ValueError, "endpoint nodes exist"):
            graph.with_edge(
                ActiveCognitiveEdge(
                    edge_id="edge-1",
                    source_id="node-a",
                    target_id="node-missing",
                    relation=EdgeRelation.IS_A,
                    source_system="perception",
                    logical_step=1,
                    evidence_ids=("evidence-1",),
                )
            )


class InMemoryActiveCognitionRuntimeTests(unittest.TestCase):
    def test_perception_boost_spread_decay_and_working_memory(self) -> None:
        runtime = InMemoryActiveCognitionRuntime(policy(), working_capacity=2)
        runtime.add_perceived_node(node("node-a", logical_step=1))
        runtime.add_perceived_node(node("node-b", logical_step=1))
        runtime.add_edge(
            ActiveCognitiveEdge(
                edge_id="edge-1",
                source_id="node-a",
                target_id="node-b",
                relation=EdgeRelation.ASSOCIATED_WITH,
                source_system="perception",
                logical_step=1,
                evidence_ids=("evidence-1",),
            )
        )
        runtime.add_perceived_node(node("node-a", logical_step=1))

        node_a = runtime.graph.get_node("node-a")
        node_b = runtime.graph.get_node("node-b")
        assert node_a is not None and node_b is not None
        self.assertGreaterEqual(node_a.activation_ppm, 500_000)
        self.assertGreaterEqual(node_b.activation_ppm, 150_000)
        self.assertIn("node-a", runtime.working_memory.node_ids())

        runtime.advance(2)
        decayed_a = runtime.graph.get_node("node-a")
        assert decayed_a is not None
        self.assertLess(decayed_a.activation_ppm, node_a.activation_ppm)
        self.assertTrue(
            any(record.reason is ActivationReason.LOGICAL_TICK_DECAY for record in runtime.activation_records)
        )

    def test_capacity_eviction_prefers_higher_activation(self) -> None:
        runtime = InMemoryActiveCognitionRuntime(
            policy(perception_boost_ppm=700_000, working_threshold_ppm=200_000),
            working_capacity=2,
        )
        runtime.add_perceived_node(node("node-a", logical_step=1))
        runtime.add_perceived_node(node("node-b", logical_step=1))
        self.assertEqual(set(runtime.working_memory.node_ids()), {"node-a", "node-b"})

        runtime.advance(2)
        runtime.add_perceived_node(node("node-c", logical_step=2))

        working_ids = set(runtime.working_memory.node_ids())
        self.assertEqual(len(working_ids), 2)
        self.assertIn("node-c", working_ids)
        self.assertNotIn("node-b", working_ids)
        self.assertTrue(any(record.node_id == "node-b" for record in runtime.eviction_records))

    def test_primed_memory_holds_subthreshold_candidates(self) -> None:
        runtime = InMemoryActiveCognitionRuntime(
            policy(
                perception_boost_ppm=250_000,
                working_threshold_ppm=400_000,
                primed_threshold_ppm=150_000,
            ),
            working_capacity=1,
        )
        runtime.add_perceived_node(node("node-a", logical_step=1))
        runtime.add_perceived_node(node("node-b", logical_step=1))

        self.assertEqual(len(runtime.working_memory.items), 0)
        self.assertEqual(len(runtime.primed_memory.items), 2)

    def test_snapshot_replay_is_deterministic(self) -> None:
        operations = (
            {
                "op": "add_perceived_node",
                "node": {
                    "node_id": "node-a",
                    "category": NodeCategory.ENTITY,
                    "source_system": "perception",
                    "logical_step": 1,
                    "evidence_ids": ("evidence-1",),
                },
            },
            {
                "op": "add_perceived_node",
                "node": {
                    "node_id": "node-b",
                    "category": NodeCategory.ENTITY,
                    "source_system": "perception",
                    "logical_step": 1,
                    "evidence_ids": ("evidence-1",),
                },
            },
            {
                "op": "add_edge",
                "edge": {
                    "edge_id": "edge-1",
                    "source_id": "node-a",
                    "target_id": "node-b",
                    "relation": EdgeRelation.ASSOCIATED_WITH,
                    "source_system": "perception",
                    "logical_step": 1,
                    "evidence_ids": ("evidence-1",),
                },
            },
            {"op": "advance", "logical_step": 2},
        )
        first = InMemoryActiveCognitionRuntime.replay(
            policy(),
            working_capacity=2,
            operations=operations,
        )
        second = InMemoryActiveCognitionRuntime.replay(
            policy(),
            working_capacity=2,
            operations=operations,
        )
        self.assertEqual(first.digest(), second.digest())

    def test_snapshot_projects_into_cognitive_state_v1(self) -> None:
        runtime = InMemoryActiveCognitionRuntime(policy(), working_capacity=2)
        runtime.add_perceived_node(node("node-a", logical_step=3))
        snapshot = runtime.snapshot()
        state = snapshot.to_cognitive_state(state_id="state-active-3")

        self.assertIsInstance(state, CognitiveState)
        self.assertEqual(state.logical_step, 3)
        self.assertEqual(len(state.memories), len(snapshot.working_memory.items))
        self.assertTrue(all(item.kind is ReferenceKind.MEMORY for item in state.memories))
        self.assertTrue(all(item.memory_kind is MemoryKind.EPISODIC for item in state.memories))
        payload = state.to_dict()
        self.assertTrue({"text", "prompt", "reward", "selected_action"}.isdisjoint(payload))

    def test_different_policies_change_activation(self) -> None:
        high = InMemoryActiveCognitionRuntime(
            policy(perception_boost_ppm=800_000),
            working_capacity=2,
        )
        low = InMemoryActiveCognitionRuntime(
            policy(perception_boost_ppm=200_000),
            working_capacity=2,
        )
        high.add_perceived_node(node("node-a", logical_step=1))
        low.add_perceived_node(node("node-a", logical_step=1))
        high_node = high.graph.get_node("node-a")
        low_node = low.graph.get_node("node-a")
        assert high_node is not None and low_node is not None
        self.assertGreater(high_node.activation_ppm, low_node.activation_ppm)

    def test_rejects_forbidden_identifiers(self) -> None:
        with self.assertRaisesRegex(ValueError, "forbidden marker"):
            node("hidden-node", logical_step=1)

    def test_runtime_nodes_are_immutable_via_graph(self) -> None:
        runtime = InMemoryActiveCognitionRuntime(policy(), working_capacity=2)
        runtime.add_perceived_node(node("node-a", logical_step=1))
        graph_node = runtime.graph.get_node("node-a")
        assert graph_node is not None
        with self.assertRaises(dataclasses.FrozenInstanceError):
            graph_node.activation_ppm = 1  # type: ignore[misc]

    def test_activation_records_include_perception_and_spreading(self) -> None:
        runtime = InMemoryActiveCognitionRuntime(policy(), working_capacity=2)
        runtime.add_perceived_node(node("node-a", logical_step=1))
        runtime.add_perceived_node(node("node-b", logical_step=1))
        runtime.add_edge(
            ActiveCognitiveEdge(
                edge_id="edge-1",
                source_id="node-a",
                target_id="node-b",
                relation=EdgeRelation.ASSOCIATED_WITH,
                source_system="perception",
                logical_step=1,
                evidence_ids=("evidence-1",),
            )
        )
        runtime.add_perceived_node(node("node-a", logical_step=1))
        sources = {record.source for record in runtime.activation_records}
        self.assertIn(ActivationSource.PERCEPTION, sources)
        self.assertIn(ActivationSource.SPREADING, sources)
        self.assertEqual(json.loads(runtime.snapshot().canonical_json())["schema_version"], "active_cognition_snapshot.v1")


if __name__ == "__main__":
    unittest.main()
