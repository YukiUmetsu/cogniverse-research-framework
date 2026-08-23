import unittest

from cogniverse_framework.replay import (
    ancestry_path,
    audit_sequence_divergence,
    classify_transition_divergence,
    find_later,
    first_divergence,
    first_reach_parents,
    post_divergence_budget,
    shared_ancestry,
)


class TestReplayDivergenceAudit(unittest.TestCase):

    def test_first_divergence_and_shared_ancestry(self):
        left = ["a", "b", "c"]
        right = ["a", "b", "x"]

        divergence = first_divergence(left, right)
        ancestry = shared_ancestry(left, right)

        self.assertEqual(divergence.index, 2)
        self.assertEqual(ancestry.shared_length, 2)

    def test_classify_transition_divergence(self):
        left = {
            "before_state_id": "s1",
            "action_id": 0,
            "after_state_id": "a1",
        }
        right_state = {
            "before_state_id": "s2",
            "action_id": 0,
            "after_state_id": "a2",
        }
        right_action = {
            "before_state_id": "s1",
            "action_id": 1,
            "after_state_id": "a3",
        }
        right_outcome = {
            "before_state_id": "s1",
            "action_id": 0,
            "after_state_id": "a9",
        }

        self.assertEqual(
            classify_transition_divergence(left, right_state),
            "different_frontier_state",
        )
        self.assertEqual(
            classify_transition_divergence(left, right_action),
            "different_action_same_state",
        )
        self.assertEqual(
            classify_transition_divergence(left, right_outcome),
            "different_outcome_same_state_action",
        )

    def test_audit_sequence_divergence_and_later_lookup(self):
        left = [
            {"before_state_id": "s0", "action_id": 0, "after_state_id": "s1"},
            {"before_state_id": "state_a", "action_id": 0, "after_state_id": "x"},
            {"before_state_id": "s2", "action_id": 1, "after_state_id": "s3"},
        ]
        right = [
            {"before_state_id": "s0", "action_id": 0, "after_state_id": "s1"},
            {"before_state_id": "state_b", "action_id": 0, "after_state_id": "y"},
            {"before_state_id": "state_a", "action_id": 0, "after_state_id": "x"},
        ]

        audit = audit_sequence_divergence(
            left,
            right,
            identity=lambda event: (
                event["before_state_id"],
                event["action_id"],
                event["after_state_id"],
            ),
            classify=classify_transition_divergence,
        )

        self.assertFalse(audit.identical)
        self.assertEqual(audit.shared_length, 1)
        self.assertEqual(audit.divergence.index, 1)
        self.assertEqual(
            audit.divergence.classification,
            "different_frontier_state",
        )
        self.assertTrue(audit.left_divergent_later_in_right.found)
        self.assertEqual(audit.left_divergent_later_in_right.indices, (2,))

        later = find_later(
            right,
            left[1],
            start=1,
            key=lambda event: event["before_state_id"],
        )
        self.assertEqual(later.indices, (2,))

    def test_post_divergence_budget_and_ancestry(self):
        events = [
            {"category": "new", "carry": "yes"},
            {"category": "familiar", "carry": "no"},
            {"category": "familiar", "carry": "yes"},
        ]
        budget = post_divergence_budget(
            events,
            1,
            category_getters={
                "category": lambda event: event["category"],
                "carry": lambda event: event["carry"],
            },
        )
        self.assertEqual(budget["category"]["familiar"], 2)
        self.assertEqual(budget["carry"]["yes"], 1)

        parents = first_reach_parents(
            [("root", "child"), ("child", "grandchild")],
            root="root",
        )
        self.assertEqual(
            ancestry_path(parents, "grandchild"),
            ["root", "child", "grandchild"],
        )


if __name__ == "__main__":
    unittest.main()
