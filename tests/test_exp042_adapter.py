import unittest

from cogniverse_framework.adapters.exp042 import Exp042Replay


class TestExp042Adapter(unittest.TestCase):

    def test_replay_classification(self):
        result = Exp042Replay().classify({
            "minigrid_reset_or_step_called": False
        })

        self.assertEqual(
            result["classification"],
            "REPLAY_ONLY",
        )

    def test_seed_compare(self):
        result = Exp042Replay().compare(
            {1: "a"},
            {1: "b"},
        )

        self.assertEqual(
            result["changed_seeds"],
            [1],
        )


if __name__ == "__main__":
    unittest.main()
