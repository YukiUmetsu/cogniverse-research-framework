import unittest

from cogniverse_framework.claims import (
    EvidenceLinker,
    LearningClaim,
)

from cogniverse_framework.experiments.base_adapter import (
    ExperimentAdapter,
)

from cogniverse_framework.experiments.exp042 import (
    Exp042Adapter,
)


class TestBundle1415(unittest.TestCase):

    def test_learning_claim(self):

        claim = LearningClaim(
            "prefer_branches",
            0.8,
            ["a"],
        )

        self.assertTrue(
            claim.validate()["valid"]
        )

    def test_evidence_linker(self):

        result = EvidenceLinker().build(
            "strategy",
            ["a", "b"],
            ["c"],
        )

        self.assertEqual(
            result["confidence"],
            0.667,
        )

    def test_adapter_contract(self):

        result = Exp042Adapter().run()

        self.assertIn(
            "learning_evidence",
            result,
        )


if __name__ == "__main__":
    unittest.main()
