MANIFEST_TEMPLATE = """experiment_id: {experiment_id}
name: {experiment_id}

type: {experiment_type}

execution:
  mode: replay

audit:
  forbid_environment_reset: true
  require_hashes: true
"""


ADAPTER_TEMPLATE = """


class {class_name}:

    experiment_id = "{experiment_id}"

    def run(self):
        return {{
            "experiment_id": self.experiment_id,
            "status": "READY"
        }}
"""


RUNNER_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

echo "Running {experiment_id}"

PYTHONPATH=../../src python adapter.py
"""


TEST_TEMPLATE = """import unittest


class TestGeneratedExperiment(unittest.TestCase):

    def test_generated(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
"""
