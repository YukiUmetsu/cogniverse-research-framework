#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 16-20: RESEARCH PLATFORM EXTENSIONS"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.analysis.statistics import (
    success_rate,
)

from cogniverse_framework.analysis.causal import (
    estimate_effect,
)

print(json.dumps({
    "bundle": "16-20",
    "status": "PASS",
    "statistics": success_rate(42,50),
    "causal_effect": estimate_effect(
        0.51,
        0.84,
    )["effect"],
    "features": [
        "statistics",
        "causal_analysis",
        "visualization_data",
        "environment_plugins",
        "research_loop",
    ],
}, indent=2))
PY
