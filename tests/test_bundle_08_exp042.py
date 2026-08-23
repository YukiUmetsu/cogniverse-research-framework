import unittest

from cogniverse_framework.experiments.exp042 import (
    Exp042Adapter,
)


class TestBundle08(unittest.TestCase):

    def test_exp042_replay_contract(self):

        result = Exp042Adapter(
            [
                {
                    "observation": "state"
                }
            ]
        ).run()

        self.assertTrue(
            result["contract"]["valid"]
        )

    def test_mutation_analysis(self):

        result = Exp042Adapter().run()

        self.assertEqual(
            result["mutation_analysis"]
            ["changed_count"],
            2,
        )


if __name__ == "__main__":
    unittest.main()
