import unittest

from cogniverse_framework.cognition import (
    ConstraintScope,
    HardConstraint,
    HomeostaticUpdate,
    LegacyScalarRewardAdapter,
    NeedState,
    TransparentPriorityPolicy,
    ValueEstimate,
    ValueVector,
    evaluate_hard_constraints,
    rank_need_states,
)
from cogniverse_framework.replay import (
    ValueHomeostasisTrace,
    build_event_trace,
    build_value_homeostasis_trace,
    compare_event_traces,
    event_trace_to_evidence_payload,
    value_homeostasis_trace_to_evidence_payload,
)
from cogniverse_framework.cognition.backends.events import CognitiveEvent, CognitiveEventKind


class ValueHomeostasisContractTests(unittest.TestCase):
    def test_need_state_is_deterministic(self) -> None:
        need = NeedState(
            need_id="need-energy",
            source_system="fixture",
            logical_step=3,
            need_kind="energy",
            level_ppm=190_000,
            target_ppm=700_000,
            deficit_ppm=510_000,
            evidence_ids=("evidence-b", "evidence-a"),
        )
        self.assertEqual(need.evidence_ids, ("evidence-a", "evidence-b"))
        self.assertEqual(need.digest(), NeedState(
            need_id="need-energy",
            source_system="fixture",
            logical_step=3,
            need_kind="energy",
            level_ppm=190_000,
            target_ppm=700_000,
            deficit_ppm=510_000,
            evidence_ids=("evidence-b", "evidence-a"),
        ).digest())

    def test_legacy_scalar_reward_cannot_target_survival(self) -> None:
        adapter = LegacyScalarRewardAdapter(
            adapter_id="legacy-1",
            source_system="fixture",
            logical_step=1,
            target_dimension_id="task-progress",
        )
        vector = adapter.to_value_vector(
            vector_id="value-1",
            scalar_reward_ppm=500_000,
            evidence_ids=("evidence-1",),
        )
        self.assertEqual(vector.dimension_values_ppm, (("task-progress", 500_000),))
        with self.assertRaisesRegex(ValueError, "cannot target survival"):
            LegacyScalarRewardAdapter(
                adapter_id="legacy-2",
                source_system="fixture",
                logical_step=1,
                target_dimension_id="survival",
            )

    def test_value_vector_rejects_survival_dimension(self) -> None:
        with self.assertRaisesRegex(ValueError, "survival dimension"):
            ValueVector(
                vector_id="value-1",
                source_system="fixture",
                logical_step=1,
                dimension_values_ppm=(("survival", 100_000),),
            )

    def test_hard_constraint_and_estimate_records(self) -> None:
        constraint = HardConstraint(
            constraint_id="constraint-1",
            source_system="fixture",
            logical_step=2,
            scopes=(ConstraintScope.USER, ConstraintScope.SELF),
            evidence_ids=("evidence-1",),
        )
        vector = ValueVector(
            vector_id="value-1",
            source_system="fixture",
            logical_step=2,
            dimension_values_ppm=(("efficiency", 250_000),),
        )
        estimate = ValueEstimate(
            estimate_id="estimate-1",
            source_system="fixture",
            logical_step=2,
            value_vector=vector,
            uncertainty_ppm=120_000,
            horizon_steps=5,
        )
        update = HomeostaticUpdate(
            update_id="update-1",
            source_system="fixture",
            logical_step=2,
            need_id="need-energy",
            previous_level_ppm=190_000,
            new_level_ppm=250_000,
            previous_deficit_ppm=510_000,
            new_deficit_ppm=450_000,
        )
        self.assertEqual(constraint.scopes, (ConstraintScope.SELF, ConstraintScope.USER))
        self.assertEqual(estimate.value_vector.vector_id, "value-1")
        self.assertEqual(update.new_deficit_ppm, 450_000)

    def test_evaluate_hard_constraints_allow_and_block(self) -> None:
        constraint = HardConstraint(
            constraint_id="constraint-1",
            source_system="fixture",
            logical_step=2,
            scopes=(ConstraintScope.SELF,),
            blocked_subject_ids=("action-blocked",),
            evidence_ids=("evidence-1",),
        )
        allowed = evaluate_hard_constraints(
            (constraint,),
            subject_id="action-safe",
            logical_step=2,
            source_system="fixture",
        )
        blocked = evaluate_hard_constraints(
            (constraint,),
            subject_id="action-blocked",
            logical_step=2,
            source_system="fixture",
        )
        self.assertTrue(allowed.allowed)
        self.assertFalse(blocked.allowed)
        self.assertEqual(blocked.violations[0].constraint_id, "constraint-1")

    def test_rank_need_states_by_deficit_and_weight(self) -> None:
        policy = TransparentPriorityPolicy(
            policy_id="fixture-priority",
            source_system="fixture",
            need_kind_weights_ppm=(("energy", 800_000), ("safety", 400_000)),
        )
        needs = (
            NeedState(
                need_id="need-energy",
                source_system="fixture",
                logical_step=1,
                need_kind="energy",
                level_ppm=200_000,
                target_ppm=700_000,
                deficit_ppm=500_000,
            ),
            NeedState(
                need_id="need-safety",
                source_system="fixture",
                logical_step=1,
                need_kind="safety",
                level_ppm=100_000,
                target_ppm=900_000,
                deficit_ppm=800_000,
            ),
        )
        ranked = rank_need_states(needs, policy)
        self.assertEqual(ranked[0].need.need_id, "need-energy")
        self.assertGreater(ranked[0].priority_score_ppm, ranked[1].priority_score_ppm)

    def test_value_homeostasis_trace_serializes_for_evidence(self) -> None:
        need = NeedState(
            need_id="need-energy",
            source_system="fixture",
            logical_step=1,
            need_kind="energy",
            level_ppm=190_000,
            target_ppm=700_000,
            deficit_ppm=510_000,
        )
        trace = build_value_homeostasis_trace(
            source_system="fixture",
            logical_step=1,
            need_states=(need,),
        )
        payload = value_homeostasis_trace_to_evidence_payload(trace)
        self.assertEqual(payload["artifact_kind"], "value_homeostasis_trace")
        self.assertEqual(payload["trace_digest"], trace.digest())

    def test_constraint_evaluations_sort_is_fully_deterministic(self) -> None:
        blocked_a = evaluate_hard_constraints(
            (
                HardConstraint(
                    constraint_id="constraint-a",
                    source_system="fixture",
                    logical_step=1,
                    blocked_subject_ids=("action-1",),
                ),
            ),
            subject_id="action-1",
            logical_step=2,
            source_system="fixture-alpha",
        )
        blocked_b = evaluate_hard_constraints(
            (
                HardConstraint(
                    constraint_id="constraint-b",
                    source_system="fixture",
                    logical_step=1,
                    blocked_subject_ids=("action-1",),
                ),
            ),
            subject_id="action-1",
            logical_step=2,
            source_system="fixture-beta",
        )
        first = build_value_homeostasis_trace(
            source_system="fixture",
            logical_step=2,
            constraint_evaluations=(blocked_b, blocked_a),
        )
        second = build_value_homeostasis_trace(
            source_system="fixture",
            logical_step=2,
            constraint_evaluations=(blocked_a, blocked_b),
        )
        self.assertEqual(first.constraint_evaluations, second.constraint_evaluations)
        self.assertEqual(first.digest(), second.digest())

    def test_value_homeostasis_trace_round_trip_preserves_all_fields(self) -> None:
        need = NeedState(
            need_id="need-energy",
            source_system="fixture",
            logical_step=3,
            need_kind="energy",
            level_ppm=190_000,
            target_ppm=700_000,
            deficit_ppm=510_000,
        )
        vector = ValueVector(
            vector_id="value-1",
            source_system="fixture",
            logical_step=3,
            dimension_values_ppm=(("efficiency", 250_000),),
        )
        estimate = ValueEstimate(
            estimate_id="estimate-1",
            source_system="fixture",
            logical_step=3,
            value_vector=vector,
            uncertainty_ppm=120_000,
            horizon_steps=4,
        )
        constraint = HardConstraint(
            constraint_id="constraint-1",
            source_system="fixture",
            logical_step=3,
            blocked_subject_ids=("action-blocked",),
        )
        evaluation = evaluate_hard_constraints(
            (constraint,),
            subject_id="action-blocked",
            logical_step=3,
            source_system="fixture",
        )
        original = build_value_homeostasis_trace(
            source_system="fixture",
            logical_step=3,
            need_states=(need,),
            value_vectors=(vector,),
            value_estimates=(estimate,),
            constraint_evaluations=(evaluation,),
        )
        restored = ValueHomeostasisTrace.from_dict(original.to_dict())
        self.assertEqual(restored.to_dict(), original.to_dict())
        self.assertEqual(restored.digest(), original.digest())


class CognitiveEventReplayTests(unittest.TestCase):
    def test_event_trace_serializes_for_evidence(self) -> None:
        events = (
            CognitiveEvent(
                event_id="event-000001",
                kind=CognitiveEventKind.PERCEPT_RECEIVED,
                logical_step=1,
                source_system="fixture",
                subject_id="percept.event-1",
                evidence_ids=("event-1",),
            ),
            CognitiveEvent(
                event_id="event-000002",
                kind=CognitiveEventKind.MEMORY_RETRIEVED,
                logical_step=1,
                source_system="fixture",
                subject_id="memory.episode-1",
                evidence_ids=("evidence-1",),
            ),
        )
        trace = build_event_trace(events, source_system="fixture")
        payload = event_trace_to_evidence_payload(trace)
        self.assertEqual(payload["trace_digest"], trace.digest())
        self.assertEqual(len(payload["trace"]["events"]), 2)

    def test_compare_event_traces_reports_divergence(self) -> None:
        left = build_event_trace(
            (
                CognitiveEvent(
                    event_id="event-000001",
                    kind=CognitiveEventKind.PERCEPT_RECEIVED,
                    logical_step=1,
                    source_system="fixture",
                    subject_id="percept.event-1",
                ),
            ),
            source_system="fixture",
        )
        right = build_event_trace(
            (
                CognitiveEvent(
                    event_id="event-000001",
                    kind=CognitiveEventKind.NODE_ACTIVATED,
                    logical_step=1,
                    source_system="fixture",
                    subject_id="percept.event-1",
                ),
            ),
            source_system="fixture",
        )
        comparison = compare_event_traces(left, right)
        self.assertFalse(comparison["equal"])
        self.assertEqual(comparison["first_divergence_index"], 0)


if __name__ == "__main__":
    unittest.main()
