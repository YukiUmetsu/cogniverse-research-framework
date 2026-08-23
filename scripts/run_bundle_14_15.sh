#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 14-15: LEARNING CLAIMS AND UNIVERSAL ADAPTER"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.experiments.exp042 import (
    Exp042Adapter,
)

from cogniverse_framework.claims import (
    EvidenceLinker,
)

result = Exp042Adapter().run()

claim = EvidenceLinker().build(
    result["learning_evidence"]["strategy"],
    result["learning_evidence"]["supporting_states"],
)

print(json.dumps({
    "bundle": "14-15",
    "status": "PASS",
    "experiment": "exp042",
    "claim": claim,
}, indent=2))
PY
