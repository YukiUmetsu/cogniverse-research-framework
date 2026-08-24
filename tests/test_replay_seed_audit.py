import unittest

from cogniverse_framework.replay import (
    SeedProfile,
    build_seed_audit_card,
    build_seed_audit_cards,
    compare_seed_audits,
    contrast_seed_to_references,
)


class TestSeedAuditCards(unittest.TestCase):
    def test_build_card_with_reference_deltas(self):
        hard = SeedProfile(
            seed=51000,
            metrics={"carried_contexts": 21, "carrying_fraction": 0.30},
            milestones={"mutation": None, "acquire": 93},
            outcome="failure",
        )
        success = SeedProfile(
            seed=51001,
            metrics={"carried_contexts": 39, "carrying_fraction": 0.53},
            milestones={"mutation": 299, "acquire": 88},
            outcome="success",
        )
        card = build_seed_audit_card(
            hard,
            failure_labels=("post_acquisition_carried_context_under_exploration",),
            reference=success,
        )
        self.assertEqual(card.schema_version, "seed_audit_card.v1")
        self.assertEqual(card.reference_seed, 51001)
        self.assertEqual(card.metric_deltas_vs_reference["carried_contexts"], -18.0)
        self.assertIn(
            "post_acquisition_carried_context_under_exploration",
            card.failure_labels,
        )

    def test_contrast_picks_nearest_reference(self):
        hard = SeedProfile(seed=51002, metrics={"carried_contexts": 23, "nonmotion": 76})
        near = SeedProfile(seed=51003, metrics={"carried_contexts": 27, "nonmotion": 72})
        far = SeedProfile(seed=51005, metrics={"carried_contexts": 41, "nonmotion": 124})
        contrast = contrast_seed_to_references(hard, (near, far))
        self.assertEqual(contrast.reference_seed, 51003)
        self.assertEqual(contrast.metric_deltas["carried_contexts"], -4.0)

    def test_compare_seed_audits_metric_and_milestone_deltas(self):
        left = (
            SeedProfile(
                seed=51000,
                metrics={"carried_contexts": 21},
                milestones={"mutation": None, "acquire": 90},
                outcome="failure",
            ),
            SeedProfile(
                seed=51001,
                metrics={"carried_contexts": 39},
                milestones={"mutation": 200, "acquire": 80},
                outcome="success",
            ),
        )
        right = (
            SeedProfile(
                seed=51000,
                metrics={"carried_contexts": 35},
                milestones={"mutation": 180, "acquire": 90},
                outcome="success",
            ),
            SeedProfile(
                seed=51001,
                metrics={"carried_contexts": 40},
                milestones={"mutation": 210, "acquire": 80},
                outcome="success",
            ),
        )
        deltas = compare_seed_audits(left, right)
        by_seed = {delta.seed: delta for delta in deltas}
        self.assertEqual(by_seed[51000].metric_deltas["carried_contexts"], 14.0)
        self.assertEqual(by_seed[51000].left_outcome, "failure")
        self.assertEqual(by_seed[51000].right_outcome, "success")
        self.assertIn("mutation", by_seed[51000].right_only_milestones)
        self.assertEqual(by_seed[51001].milestone_deltas["mutation"], 10)

    def test_build_seed_audit_cards_attaches_nearest_success(self):
        profiles = (
            SeedProfile(
                seed=51000,
                metrics={"carried_contexts": 21},
                outcome="failure",
            ),
            SeedProfile(
                seed=51001,
                metrics={"carried_contexts": 39},
                outcome="success",
            ),
            SeedProfile(
                seed=51002,
                metrics={"carried_contexts": 23},
                outcome="failure",
            ),
        )
        cards = build_seed_audit_cards(
            profiles,
            failure_labels_by_seed={
                51000: ("under_explored",),
                51002: ("under_explored",),
            },
        )
        by_seed = {card.seed: card for card in cards}
        self.assertEqual(by_seed[51000].reference_seed, 51001)
        self.assertEqual(by_seed[51002].reference_seed, 51001)
        self.assertIsNone(by_seed[51001].reference_seed)


if __name__ == "__main__":
    unittest.main()
