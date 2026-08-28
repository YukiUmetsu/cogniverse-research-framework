import unittest

from cogniverse_framework.cognition import (
    ConstraintScope,
    HardConstraint,
    HomeostaticUpdate,
    LegacyScalarRewardAdapter,
    NeedState,
    ValueEstimate,
    ValueVector,
)
from cogniverse_framework.replay import (
    build_event_trace,
    compare_event_traces,
    event_trace_to_evidence_payload,
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
