import unittest

from cogniverse_framework.replay.transition import (
    Transition,
)

from cogniverse_framework.replay.trajectory import (
    Trajectory,
)

from cogniverse_framework.learning.extractor import (
    BehaviorExtractor,
)


class TestBundle13(unittest.TestCase):

    def test_extract_strategy(self):

        trajectory = Trajectory()

        trajectory.add(
            Transition(
                "790ffc07",
                "continue_branch",
                "success",
            )
        )

        result = BehaviorExtractor().extract(
            trajectory
        )

        self.assertEqual(
            result["strategy"],
            "prefer_promising_branches",
        )


if __name__ == "__main__":
    unittest.main()
