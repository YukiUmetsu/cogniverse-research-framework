#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 09: GENERATED EXP-042 INTEGRATION"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

rm -rf .runtime/bundle09

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.integration import (
    ExperimentRunner,
)

result = ExperimentRunner(
    "exp042"
).run(
    ".runtime/bundle09"
)

print(json.dumps({
    "bundle": "09",
    "experiment": result["experiment"],
    "status": result["result"]["status"],
    "artifacts": len(
        result["artifact_manifest"]["files"]
    ),
}, indent=2))
PY
