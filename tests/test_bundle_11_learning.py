import unittest

from cogniverse_framework.learning import (
    BehaviorTrace,
    KnowledgeState,
    StrategyTrace,
)

from cogniverse_framework.analysis import (
    compare_knowledge,
)


class TestBundle11(unittest.TestCase):

    def test_behavior_trace(self):

        trace = BehaviorTrace(
            "state-a",
            "continue",
            "move",
            "success",
        )

        self.assertEqual(
            trace.to_dict()["state"],
            "state-a",
        )

    def test_knowledge_delta(self):

        before = KnowledgeState()

        before.add_strategy(
            "random_exploration"
        )

        after = KnowledgeState()

        after.add_strategy(
            "information_guided_exploration"
        )

        result = compare_knowledge(
            before.snapshot(),
            after.snapshot(),
        )

        self.assertIn(
            "information_guided_exploration",
            result["new_strategies"],
        )


if __name__ == "__main__":
    unittest.main()
