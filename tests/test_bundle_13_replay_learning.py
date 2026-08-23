import unittest

from cogniverse_framework.learning.extractor import BehaviorExtractor
from cogniverse_framework.replay.trajectory import Trajectory
from cogniverse_framework.replay.transition import Transition


class TestBundle13(unittest.TestCase):

    def test_extract_strategy(self):
        trajectory = Trajectory()
        trajectory.add(
            Transition("790ffc07", "continue_branch", "success")
        )

        result = BehaviorExtractor(
            continue_branch_strategy="prefer_promising_branches",
        ).extract(trajectory)

        self.assertEqual(result["strategy"], "prefer_promising_branches")

    def test_default_strategy_is_generic(self):
        trajectory = Trajectory()
        trajectory.add(
            Transition("state", "continue_branch", "success")
        )

        result = BehaviorExtractor().extract(trajectory)
        self.assertEqual(result["strategy"], "continue_successful_branch")


if __name__ == "__main__":
    unittest.main()
