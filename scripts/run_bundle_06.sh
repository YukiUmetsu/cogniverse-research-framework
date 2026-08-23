#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 06: EXECUTION PIPELINE"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.execution.engine import (
    ExecutionEngine,
)


class Adapter:

    def run(self):
        return {
            "experiment": "bundle06",
            "status": "ok",
        }


result = ExecutionEngine(
    Adapter()
).run()

print(json.dumps({
    "bundle": "06",
    "execution_engine": "PASS",
    "status": result["status"],
    "phases": list(result["phases"].keys()),
}, indent=2))
PY
