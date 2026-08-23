#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 10: EVIDENCE AND REPRODUCIBILITY"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

rm -rf .runtime/bundle10

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.evidence import (
    RunRecord,
    EvidenceStore,
)

from cogniverse_framework.comparison import (
    compare_runs,
)

record = RunRecord(
    "exp042",
    "COMPLETE",
).create()

artifact = EvidenceStore(
    ".runtime/bundle10"
).write(
    "run.json",
    record,
)

comparison = compare_runs(
    {"mutation": 1},
    {"mutation": 2},
)

print(json.dumps({
    "bundle": "10",
    "evidence": "PASS",
    "run_id": record["run_id"],
    "hash_created": "sha256" in artifact,
    "comparison": comparison["changed"],
}, indent=2))
PY
