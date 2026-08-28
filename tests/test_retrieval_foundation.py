import hashlib
import unittest

from cogniverse_framework.cognition import (
    ActivationPolicy,
    ActiveCognitiveNode,
    ActivePerceptionConsumer,
    CognitiveGap,
    GapKind,
    InformationNeed,
    InMemoryActiveCognitionRuntime,
    InMemoryRetrievalController,
    MemoryKind,
    NodeCategory,
    PerceptModality,
    PublicPercept,
    RetrievalRankingPolicy,
    detect_cognitive_gaps,
    episodic_memory_record,
    semantic_memory_record,
)


def activation_policy() -> ActivationPolicy:
    return ActivationPolicy(
        policy_id="retrieval-test-activation",
        decay_ppm=900_000,
        perception_boost_ppm=500_000,
        spreading_boost_ppm=100_000,
        working_threshold_ppm=300_000,
        primed_threshold_ppm=100_000,
    )


def ranking_policy(**overrides) -> RetrievalRankingPolicy:
    values = dict(
        policy_id="retrieval-test-ranking",
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


def digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class RetrievalFoundationTests(unittest.TestCase):
    def test_detects_unknown_cause_for_event_without_incoming_cause(self) -> None:
        runtime = InMemoryActiveCognitionRuntime(activation_policy(), working_capacity=2)
        runtime.add_perceived_node(
            ActiveCognitiveNode(
                node_id="event-1",
                category=NodeCategory.EVENT,
                source_system="fixture",
                logical_step=1,
                evidence_ids=("evidence-1",),
            )
        )
        snapshot = runtime.snapshot()
        gaps = detect_cognitive_gaps(snapshot)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0].kind, GapKind.UNKNOWN_CAUSE)
        self.assertEqual(gaps[0].subject_node_id, "event-1")

    def test_retrieval_prefers_associative_episodic_memory_for_unknown_cause(self) -> None:
        consumer = ActivePerceptionConsumer(
            activation_policy(),
            working_capacity=2,
            node_category=NodeCategory.EVENT,
        )
        percept = PublicPercept(
            percept_id="event-1",
            modality=PerceptModality.STRUCTURED,
            source_system="fixture",
            logical_step=1,
            content_sha256=digest("event-1"),
            evidence_ids=("evidence-1",),
        )
        consumer.receive(percept)
        snapshot = consumer.snapshot()

        controller = InMemoryRetrievalController(ranking_policy())
        controller.store(
            episodic_memory_record(
                memory_id="episode-weak",
                source_system="fixture-memory",
                logical_step=20,
                content_sha256=digest("episode-weak"),
                evidence_ids=("evidence-2",),
                related_node_ids=("other-node",),
            )
        )
        controller.store(
            episodic_memory_record(
                memory_id="episode-strong",
                source_system="fixture-memory",
                logical_step=1,
                content_sha256=digest("episode-strong"),
                evidence_ids=("evidence-3",),
                related_node_ids=("percept.event-1",),
            )
        )

        session = controller.run_for_snapshot(snapshot)
        self.assertEqual(len(session.gaps), 1)
        self.assertEqual(session.gaps[0].kind, GapKind.UNKNOWN_CAUSE)
        self.assertEqual(len(session.results), 1)
        candidates = session.results[0].candidates
        self.assertGreaterEqual(len(candidates), 1)
        self.assertEqual(candidates[0].memory_id, "episode-strong")
        self.assertGreater(candidates[0].score_ppm, 0)

    def test_retrieval_session_is_deterministic(self) -> None:
        consumer = ActivePerceptionConsumer(
            activation_policy(),
            working_capacity=2,
            node_category=NodeCategory.EVENT,
        )
        consumer.receive(
            PublicPercept(
                percept_id="event-1",
                modality=PerceptModality.STRUCTURED,
                source_system="fixture",
                logical_step=1,
                content_sha256=digest("event-1"),
                evidence_ids=("evidence-1",),
            )
        )
        snapshot = consumer.snapshot()

        def run_once():
            controller = InMemoryRetrievalController(ranking_policy())
            controller.store(
                episodic_memory_record(
                    memory_id="episode-1",
                    source_system="fixture-memory",
                    logical_step=1,
                    content_sha256=digest("episode-1"),
                    evidence_ids=("evidence-2",),
                    related_node_ids=("percept.event-1",),
                )
            )
            return controller.run_for_snapshot(snapshot)

        first = run_once()
        second = run_once()
        self.assertEqual(
            first.results[0].digest(),
            second.results[0].digest(),
        )

    def test_gap_drives_role_selection_for_belief_conflict(self) -> None:
        runtime = InMemoryActiveCognitionRuntime(activation_policy(), working_capacity=2)
        runtime.add_perceived_node(
            ActiveCognitiveNode(
                node_id="belief-a",
                category=NodeCategory.BELIEF,
                source_system="fixture",
                logical_step=1,
                evidence_ids=("evidence-1",),
            )
        )
        runtime.add_perceived_node(
            ActiveCognitiveNode(
                node_id="belief-b",
                category=NodeCategory.BELIEF,
                source_system="fixture",
                logical_step=1,
                evidence_ids=("evidence-2",),
            )
        )
        from cogniverse_framework.cognition import ActiveCognitiveEdge, EdgeRelation

        runtime.add_edge(
            ActiveCognitiveEdge(
                edge_id="edge-1",
                source_id="belief-a",
                target_id="belief-b",
                relation=EdgeRelation.CONTRADICTS,
                source_system="fixture",
                logical_step=1,
                evidence_ids=("evidence-3",),
            )
        )
        snapshot = runtime.snapshot()
        gaps = detect_cognitive_gaps(snapshot)
        self.assertTrue(any(gap.kind is GapKind.UNRESOLVED_BELIEF_CONFLICT for gap in gaps))

        controller = InMemoryRetrievalController(ranking_policy())
        controller.store(
            semantic_memory_record(
                memory_id="semantic-1",
                source_system="fixture-memory",
                logical_step=1,
                content_sha256=digest("semantic-1"),
                evidence_ids=("evidence-4",),
                related_node_ids=("belief-a",),
            )
        )
        session = controller.run_for_snapshot(snapshot)
        conflict_gap = next(
            gap for gap in session.gaps if gap.kind is GapKind.UNRESOLVED_BELIEF_CONFLICT
        )
        request = next(req for req in session.requests if req.gap.gap_id == conflict_gap.gap_id)
        self.assertIn(MemoryKind.SEMANTIC, request.memory_roles)
        self.assertGreaterEqual(len(session.results[0].candidates), 1)

    def test_memory_record_requires_provenance(self) -> None:
        from cogniverse_framework.cognition import LongTermMemoryRecord

        with self.assertRaisesRegex(ValueError, "evidence_ids"):
            LongTermMemoryRecord(
                memory_id="memory-1",
                memory_kind=MemoryKind.EPISODIC,
                source_system="fixture",
                logical_step=1,
                content_sha256=digest("x"),
                evidence_ids=(),
            )

    def test_information_need_derives_from_gap(self) -> None:
        gap = CognitiveGap(
            gap_id="gap-0001",
            kind=GapKind.MISSING_ASSOCIATION,
            subject_node_id="node-1",
            source_system="fixture",
            logical_step=2,
            urgency_ppm=600_000,
            evidence_ids=("evidence-1",),
        )
        from cogniverse_framework.cognition import InformationNeed

        need = InformationNeed.from_gap(gap)
        self.assertEqual(need.gap_id, "gap-0001")
        self.assertEqual(need.priority_ppm, 600_000)


if __name__ == "__main__":
    unittest.main()
