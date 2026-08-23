import unittest

from cogniverse_framework.execution.engine import (
    ExecutionEngine,
)


class Adapter:

    def run(self):
        return {
            "status": "ok"
        }


class TestExecutionEngine(unittest.TestCase):

    def test_pipeline(self):

        result = ExecutionEngine(
            Adapter()
        ).run()

        self.assertEqual(
            result["status"],
            "COMPLETE",
        )

        self.assertEqual(
            result["phases"]["settle"]["status"],
            "PASS",
        )


if __name__ == "__main__":
    unittest.main()
