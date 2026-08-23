import unittest

from cogniverse_framework.experiments.exp042 import Exp042Adapter


# Lab-owned fixture data (not hardcoded inside the framework adapter).
_DEMO_BASELINE = {51003: 376, 51004: 305}
_DEMO_CANDIDATE = {51003: 382, 51004: 311}
_DEMO_EVIDENCE = {
    "strategy": "prefer_promising_branches",
    "supporting_states": ["cb148158", "790ffc07"],
    "confidence": 0.8,
}


class TestBundle08(unittest.TestCase):

    def test_exp042_replay_contract(self):
        result = Exp042Adapter(
            [{"observation": "state"}],
            seed=51005,
        ).run()

        self.assertTrue(result["contract"]["valid"])

    def test_mutation_analysis(self):
        result = Exp042Adapter(
            baseline_scores=_DEMO_BASELINE,
            candidate_scores=_DEMO_CANDIDATE,
            learning_evidence=_DEMO_EVIDENCE,
        ).run()

        self.assertEqual(result["mutation_analysis"]["changed_count"], 2)


if __name__ == "__main__":
    unittest.main()
