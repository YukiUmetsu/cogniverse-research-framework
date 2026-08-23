#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 07: END TO END GENERATED EXPERIMENT"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

rm -rf .runtime/bundle07

PYTHONPATH=src python - <<'PY'
import json
import subprocess
from pathlib import Path

from cogniverse_framework.generator.generator import (
    ExperimentGenerator,
)

root = Path(".runtime/bundle07")

result = ExperimentGenerator(
    root
).generate(
    "exp043",
    "replay-analysis",
)

experiment = root / "exp043"

completed = subprocess.run(
    [
        "bash",
        str(experiment / "run.sh"),
    ],
    cwd=experiment,
    env={
        "PYTHONPATH": "../../../src"
    },
    capture_output=True,
    text=True,
)

print(json.dumps({
    "bundle": "07",
    "generator": "PASS",
    "execution_returncode": completed.returncode,
    "generated": result["experiment_id"],
}, indent=2))

if completed.returncode != 0:
    print(completed.stderr)
    raise SystemExit(1)
PY
