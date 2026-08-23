import unittest

from cogniverse_framework.adapters.exp042 import Exp042Replay
from cogniverse_framework.replay import compare_seed_matrix


class TestExp042Adapter(unittest.TestCase):

    def test_replay_classification(self):
        result = Exp042Replay().classify({
            "minigrid_reset_or_step_called": False,
        })
        self.assertEqual(result["classification"], "REPLAY_ONLY")

    def test_seed_compare(self):
        result = Exp042Replay().compare({1: "a"}, {1: "b"})
        self.assertEqual(result["changed_seeds"], [1])

    def test_compare_seed_matrix_typed(self):
        matrix = compare_seed_matrix({1: "a", 2: "x"}, {1: "b", 2: "x"})
        self.assertEqual(matrix.changed_seeds, [1])
        self.assertEqual(matrix.changed_count, 1)
        self.assertFalse(matrix.rows[1].changed)



    def test_compare_seed_matrix_mixed_seed_types(self):
        matrix = compare_seed_matrix({1: "a", "2": "x"}, {1: "b", "2": "x"})
        self.assertEqual(matrix.changed_seeds, [1])
        self.assertEqual(matrix.changed_count, 1)


if __name__ == "__main__":
    unittest.main()
