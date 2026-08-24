import unittest

from cogniverse_framework.replay import (
    SeedProfile,
    diagnose_seed_failures,
    label_if_metric_strictly_lower,
    label_if_milestone_absent_on_hard,
    profiles_from_metric_table,
)


class TestReplaySeedFailureDiagnosis(unittest.TestCase):
    def test_separates_hard_seeds_on_coverage_metric(self):
        profiles = profiles_from_metric_table(
            {
                51000: {"carried_contexts": 21, "carrying_fraction": 0.30},
                51002: {"carried_contexts": 23, "carrying_fraction": 0.46},
                51001: {"carried_contexts": 39, "carrying_fraction": 0.53},
                51005: {"carried_contexts": 41, "carrying_fraction": 0.52},
            },
            outcomes={
                51000: "failure",
                51002: "failure",
                51001: "success",
                51005: "success",
            },
            milestones={
                51000: {"mutation": None, "acquire": 93},
                51002: {"mutation": None, "acquire": 87},
                51001: {"mutation": 299, "acquire": 88},
                51005: {"mutation": 172, "acquire": 7},
            },
        )

        diagnosis = diagnose_seed_failures(
            profiles,
            hard_seeds=(51000, 51002),
            reference_seeds=(51001, 51005),
            classifiers=(
                label_if_metric_strictly_lower(
                    "carried_contexts",
                    label="post_acquisition_carried_context_under_exploration",
                ),
                label_if_milestone_absent_on_hard(
                    "mutation",
                    label="target_milestone_absent_on_hard_seeds",
                ),
            ),
        )

        self.assertIn("carried_contexts", diagnosis.separating_lower_metrics)
        self.assertIn(
            "post_acquisition_carried_context_under_exploration",
            diagnosis.classifier_labels,
        )
        self.assertIn(
            "target_milestone_absent_on_hard_seeds",
            diagnosis.classifier_labels,
        )
        carried = next(
            contrast
            for contrast in diagnosis.metric_contrasts
            if contrast.metric == "carried_contexts"
        )
        self.assertEqual(carried.hard_median, 22.0)
        self.assertEqual(carried.reference_median, 40.0)
        self.assertTrue(carried.hard_strictly_below_reference)

        mutation = next(
            contrast
            for contrast in diagnosis.milestone_contrasts
            if contrast.milestone == "mutation"
        )
        self.assertEqual(mutation.hard_present_count, 0)
        self.assertEqual(mutation.reference_present_count, 2)

    def test_defaults_reference_to_non_hard_profiles(self):
        profiles = (
            SeedProfile(seed="a", metrics={"score": 1}),
            SeedProfile(seed="b", metrics={"score": 2}),
            SeedProfile(seed="c", metrics={"score": 10}),
            SeedProfile(seed="d", metrics={"score": 12}),
        )
        diagnosis = diagnose_seed_failures(profiles, hard_seeds=("a", "b"))
        self.assertEqual(diagnosis.reference_seeds, ("c", "d"))
        self.assertEqual(diagnosis.separating_lower_metrics, ("score",))

    def test_rejects_empty_hard_or_reference(self):
        profiles = (SeedProfile(seed=1, metrics={"x": 1}),)
        with self.assertRaises(ValueError):
            diagnose_seed_failures(profiles, hard_seeds=())
        with self.assertRaises(ValueError):
            diagnose_seed_failures(profiles, hard_seeds=(1,))


if __name__ == "__main__":
    unittest.main()
