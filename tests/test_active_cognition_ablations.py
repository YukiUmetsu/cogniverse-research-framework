import hashlib
import unittest

from cogniverse_framework.cognition import (
    ActivationPolicy,
    ActiveCognitionAblationConfig,
    NodeCategory,
    PerceptModality,
    PublicPercept,
    RetrievalRankingPolicy,
    build_ablation_coordinator,
    episodic_memory_record,
    run_ablated_cycle,
)


def digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def activation_policy(**overrides) -> ActivationPolicy:
    values = dict(
        policy_id="ablation-test-activation",
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
        policy_id="ablation-test-ranking",
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


def event_percept() -> PublicPercept:
    return PublicPercept(
        percept_id="event-1",
        modality=PerceptModality.STRUCTURED,
        source_system="ablation-fixture",
        logical_step=1,
        content_sha256=digest("event-1"),
        evidence_ids=("event-1",),
    )


class ActiveCognitionAblationTests(unittest.TestCase):
    def test_disable_retrieval_skips_memory_materialization(self) -> None:
        baseline = build_ablation_coordinator(
            activation_policy(),
            ranking_policy(),
            ActiveCognitionAblationConfig(ablation_id="baseline"),
            working_capacity=4,
            node_category=NodeCategory.EVENT,
        )
        no_retrieval = build_ablation_coordinator(
            activation_policy(),
            ranking_policy(),
            ActiveCognitionAblationConfig(ablation_id="no-retrieval", retrieval_enabled=False),
            working_capacity=4,
            node_category=NodeCategory.EVENT,
        )
        for coordinator in (baseline, no_retrieval):
            coordinator.store_memory(
                episodic_memory_record(
                    memory_id="episode-1",
                    source_system="ablation-fixture",
                    logical_step=1,
                    content_sha256=digest("episode-1"),
                    evidence_ids=("evidence-1",),
                    related_node_ids=("percept.event-1",),
                )
            )

        baseline_result = run_ablated_cycle(
            baseline,
            event_percept(),
            ActiveCognitionAblationConfig(ablation_id="baseline"),
            goal_node_ids=("percept.event-1",),
        )
        no_retrieval_result = run_ablated_cycle(
            no_retrieval,
            event_percept(),
            ActiveCognitionAblationConfig(ablation_id="no-retrieval", retrieval_enabled=False),
            goal_node_ids=("percept.event-1",),
        )

        self.assertIsNotNone(baseline.runtime.graph.get_node("memory.episode-1"))
        self.assertIsNone(no_retrieval.runtime.graph.get_node("memory.episode-1"))
        self.assertNotEqual(baseline_result.to_dict(), no_retrieval_result.to_dict())

    def test_disable_spreading_changes_activation_policy(self) -> None:
        config = ActiveCognitionAblationConfig(
            ablation_id="no-spread",
            spreading_enabled=False,
        )
        policy = config.apply_activation_policy(activation_policy())
        self.assertEqual(policy.spreading_boost_ppm, 0)
        self.assertIn("no-spread", policy.policy_id)

    def test_working_capacity_override_is_deterministic(self) -> None:
        small = build_ablation_coordinator(
            activation_policy(),
            ranking_policy(),
            ActiveCognitionAblationConfig(ablation_id="small-wm", working_capacity=1),
            working_capacity=8,
            node_category=NodeCategory.EVENT,
        )
        self.assertEqual(small.runtime.working_memory.capacity, 1)


if __name__ == "__main__":
    unittest.main()
