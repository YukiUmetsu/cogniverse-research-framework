#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 08: EXP-042 MIGRATION ADAPTER"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.experiments.exp042 import (
    Exp042Adapter,
)

result = Exp042Adapter().run()

print(json.dumps({
    "bundle": "08",
    "experiment": "exp042",
    "contract": result["contract"]["valid"],
    "mutation_changes":
        result["mutation_analysis"]["changed_count"],
}, indent=2))
PY
