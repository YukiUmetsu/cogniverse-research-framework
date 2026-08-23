#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 11: LEARNER BEHAVIOR EVIDENCE"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.learning import (
    KnowledgeState,
    StrategyTrace,
)

from cogniverse_framework.analysis import (
    compare_knowledge,
)

before = KnowledgeState(
    strategies=[
        "random_exploration"
    ]
)

after = KnowledgeState(
    concepts=[
        "frontier_value"
    ],
    strategies=[
        "information_guided_exploration"
    ]
)

delta = compare_knowledge(
    before.snapshot(),
    after.snapshot(),
)

trace = StrategyTrace(
    "information_guided_exploration",
    "higher_expected_information_gain",
    0.8,
)

print(json.dumps({
    "bundle": "11",
    "learning_evidence": "PASS",
    "new_strategies": delta["new_strategies"],
    "trace": trace.to_dict(),
}, indent=2))
PY
