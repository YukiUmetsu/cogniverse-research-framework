#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 05: EXPERIMENT GENERATOR"

PYTHONPATH=src python -m unittest discover -s tests -v

rm -rf .runtime/bundle05_generated

PYTHONPATH=src python - <<'PY'
from cogniverse_framework.generator.generator import ExperimentGenerator
import json

result = ExperimentGenerator(
    ".runtime/bundle05_generated"
).generate(
    "exp043",
    "replay-analysis",
)

print(json.dumps({
    "bundle": "05",
    "generator": "PASS",
    "experiment": result["experiment_id"],
    "files": len(result["files"]),
}, indent=2))
PY
