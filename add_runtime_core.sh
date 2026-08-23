#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/experiments \
  src/cogniverse_framework/cli

cat > src/cogniverse_framework/experiments/execution_result.py <<'PY'
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionResult:
    experiment_id: str
    status: str
    phase_results: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "experiment_id": self.experiment_id,
            "status": self.status,
            "phase_results": self.phase_results,
            "artifacts": self.artifacts,
        }
PY

cat > src/cogniverse_framework/experiments/lifecycle.py <<'PY'
from typing import Protocol


class ExperimentLifecycle(Protocol):
    def preflight(self) -> dict:
        ...

    def execute(self) -> dict:
        ...

    def analyze(self) -> dict:
        ...

    def settle(self) -> dict:
        ...
PY

cat > src/cogniverse_framework/experiments/runner.py <<'PY'
from .execution_result import ExecutionResult


class ExperimentRunner:

    def __init__(self, experiment_id, lifecycle):
        self.experiment_id = experiment_id
        self.lifecycle = lifecycle

    def run(self):
        result = ExecutionResult(
            experiment_id=self.experiment_id,
            status="RUNNING",
        )

        result.phase_results["preflight"] = (
            self.lifecycle.preflight()
        )

        result.phase_results["execute"] = (
            self.lifecycle.execute()
        )

        result.phase_results["analyze"] = (
            self.lifecycle.analyze()
        )

        result.phase_results["settle"] = (
            self.lifecycle.settle()
        )

        result.status = "COMPLETE"

        return result
PY

cat > src/cogniverse_framework/experiments/example.py <<'PY'
class ExampleExperiment:

    def preflight(self):
        return {
            "status": "PASS",
            "environment_reset": False,
        }

    def execute(self):
        return {
            "executed": False,
            "mode": "example",
        }

    def analyze(self):
        return {
            "analysis": "example",
        }

    def settle(self):
        return {
            "settled": True,
        }
PY

cat > src/cogniverse_framework/cli/run.py <<'PY'
from cogniverse_framework.experiments.runner import ExperimentRunner
from cogniverse_framework.experiments.example import ExampleExperiment
import json


def main():
    runner = ExperimentRunner(
        "example-exp",
        ExampleExperiment(),
    )

    print(json.dumps(
        runner.run().to_dict(),
        indent=2,
    ))


if __name__ == "__main__":
    main()
PY

cat > src/cogniverse_framework/cli/__init__.py <<'PY'
PY

echo "Runtime core added"
