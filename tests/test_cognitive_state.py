import dataclasses
import json
import unittest

from cogniverse_framework.cognition.state import (
    CognitiveReference,
    CognitiveState,
    MemoryKind,
    ReferenceKind,
)


def ref(
    ref_id: str,
    kind: ReferenceKind,
    *,
    confidence_ppm: int | None = 800_000,
    memory_kind: MemoryKind | None = None,
) -> CognitiveReference:
    return CognitiveReference(
        ref_id=ref_id,
        kind=kind,
        source_system="fixture",
        logical_step=4,
        confidence_ppm=confidence_ppm,
        evidence_ids=("evidence-b", "evidence-a"),
        memory_kind=memory_kind,
    )


def complete_state(*, reverse: bool = False) -> CognitiveState:
    values = {
        "goals": (ref("goal-1", ReferenceKind.GOAL),),
        "needs": (ref("need-1", ReferenceKind.NEED),),
        "beliefs": (ref("belief-1", ReferenceKind.BELIEF),),
        "predictions": (ref("prediction-1", ReferenceKind.PREDICTION),),
        "memories": (
            ref(
                "memory-2",
                ReferenceKind.MEMORY,
                memory_kind=MemoryKind.SEMANTIC,
            ),
            ref(
                "memory-1",
                ReferenceKind.MEMORY,
                memory_kind=MemoryKind.EPISODIC,
            ),
        ),
        "possible_actions": (ref("action-1", ReferenceKind.ACTION),),
    }
    if reverse:
        values = {key: tuple(reversed(items)) for key, items in values.items()}
    return CognitiveState(
        state_id="state-1",
        logical_step=5,
        uncertainty_ppm=250_000,
        hard_constraint_ids=("constraint-b", "constraint-a"),
        **values,
    )


class CognitiveReferenceTests(unittest.TestCase):
    def test_normalizes_evidence_ids(self) -> None:
        item = ref("belief-1", ReferenceKind.BELIEF)
        self.assertEqual(item.evidence_ids, ("evidence-a", "evidence-b"))

    def test_requires_memory_kind_only_for_memory_references(self) -> None:
        with self.assertRaisesRegex(ValueError, "memory_kind is required"):
            ref("memory-1", ReferenceKind.MEMORY)
        with self.assertRaisesRegex(ValueError, "memory_kind is only valid"):
            ref(
                "belief-1",
                ReferenceKind.BELIEF,
                memory_kind=MemoryKind.SEMANTIC,
            )

    def test_rejects_invalid_confidence_and_forbidden_identifiers(self) -> None:
        with self.assertRaisesRegex(ValueError, "confidence_ppm"):
            ref("belief-1", ReferenceKind.BELIEF, confidence_ppm=1_000_001)
        with self.assertRaisesRegex(ValueError, "forbidden marker"):
            ref("hidden-answer", ReferenceKind.BELIEF)


class CognitiveStateTests(unittest.TestCase):
    def test_serialization_and_digest_are_deterministic(self) -> None:
        first = complete_state()
        second = complete_state(reverse=True)
        self.assertEqual(first.canonical_json(), second.canonical_json())
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(first.hard_constraint_ids, ("constraint-a", "constraint-b"))
        self.assertEqual(
            tuple(item.ref_id for item in first.memories),
            ("memory-1", "memory-2"),
        )
        self.assertEqual(json.loads(first.canonical_json()), first.to_dict())

    def test_has_only_typed_coordination_fields(self) -> None:
        payload = complete_state().to_dict()
        self.assertEqual(payload["schema_version"], "cognitive_state.v1")
        self.assertEqual(
            set(payload),
            {
                "schema_version",
                "state_id",
                "logical_step",
                "goals",
                "needs",
                "beliefs",
                "predictions",
                "memories",
                "possible_actions",
                "uncertainty_ppm",
                "hard_constraint_ids",
            },
        )
        self.assertTrue(
            {"text", "prompt", "reasoning", "reward", "selected_action"}.isdisjoint(payload)
        )

    def test_rejects_wrong_collection_kind(self) -> None:
        values = complete_state().to_dict()
        del values
        with self.assertRaisesRegex(ValueError, "goals must contain only goal"):
            CognitiveState(
                state_id="state-1",
                logical_step=5,
                goals=(ref("belief-1", ReferenceKind.BELIEF),),
            )

    def test_rejects_duplicate_reference_ids_across_collections(self) -> None:
        with self.assertRaisesRegex(ValueError, "reference IDs must be unique"):
            CognitiveState(
                state_id="state-1",
                logical_step=5,
                goals=(ref("same-id", ReferenceKind.GOAL),),
                beliefs=(ref("same-id", ReferenceKind.BELIEF),),
            )

    def test_is_immutable_and_rejects_invalid_state_values(self) -> None:
        state = complete_state()
        with self.assertRaises(dataclasses.FrozenInstanceError):
            state.logical_step = 6  # type: ignore[misc]
        with self.assertRaisesRegex(ValueError, "logical_step"):
            CognitiveState(state_id="state-1", logical_step=-1)
        with self.assertRaisesRegex(ValueError, "uncertainty_ppm"):
            CognitiveState(
                state_id="state-1",
                logical_step=0,
                uncertainty_ppm=-1,
            )


if __name__ == "__main__":
    unittest.main()
