import unittest

from cogniverse_framework.integration.learning_pipeline import (
    LearningPipeline,
)


class TestBundle12(unittest.TestCase):

    def test_learning_pipeline(self):

        result = LearningPipeline(
            "exp042"
        ).run()

        self.assertEqual(
            result["experiment"],
            "exp042",
        )

        self.assertIn(
            "information_guided_exploration",
            result["behavior_change"]["new_strategies"],
        )


if __name__ == "__main__":
    unittest.main()
