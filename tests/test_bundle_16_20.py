import unittest

from cogniverse_framework.analysis.statistics import (
    success_rate,
    confidence_range,
)

from cogniverse_framework.analysis.causal import (
    estimate_effect,
)

from cogniverse_framework.environments.registry import (
    EnvironmentRegistry,
)

from cogniverse_framework.environments.minigrid import (
    MiniGridAdapter,
)

from cogniverse_framework.runner.queue import (
    ExperimentQueue,
)

from cogniverse_framework.runner.loop import (
    ResearchLoop,
)


class TestBundle1620(unittest.TestCase):

    def test_statistics(self):

        self.assertEqual(
            success_rate(8,10),
            0.8,
        )

        self.assertIn(
            "lower",
            confidence_range(8,10),
        )

    def test_causal(self):

        self.assertEqual(
            estimate_effect(
                0.5,
                0.8,
            )["effect"],
            0.3,
        )

    def test_environment(self):

        registry = EnvironmentRegistry()

        registry.register(
            MiniGridAdapter()
        )

        self.assertEqual(
            registry.get("minigrid").environment_id,
            "minigrid",
        )

    def test_runner(self):

        queue = ExperimentQueue()

        queue.add("exp042")

        result = ResearchLoop(
            queue
        ).run_once()

        self.assertEqual(
            result["status"],
            "COMPLETE",
        )


if __name__ == "__main__":
    unittest.main()
