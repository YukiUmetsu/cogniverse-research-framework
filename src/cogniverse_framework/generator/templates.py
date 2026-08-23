MANIFEST_TEMPLATE = """experiment_id: {experiment_id}
name: {experiment_id}
type: {experiment_type}

execution:
  mode: framework

audit:
  forbid_environment_reset: true
  require_hashes: true
"""


ADAPTER_TEMPLATE = """from cogniverse_framework.execution.engine import ExecutionEngine


class {class_name}:

    experiment_id = "{experiment_id}"

    def run(self):
        return {{
            "experiment_id": self.experiment_id,
            "result": "ok"
        }}


if __name__ == "__main__":

    result = ExecutionEngine(
        {class_name}()
    ).run()

    print(result)
"""


RUNNER_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

PYTHONPATH="$ROOT/src" python3 adapter.py
"""


TEST_TEMPLATE = """import unittest


class TestGeneratedExperiment(unittest.TestCase):

    def test_generated(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
"""
