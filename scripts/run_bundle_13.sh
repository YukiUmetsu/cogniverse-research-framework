#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 13: REPLAY DERIVED LEARNER EVIDENCE"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.replay.transition import (
    Transition,
)

from cogniverse_framework.replay.trajectory import (
    Trajectory,
)

from cogniverse_framework.learning.extractor import (
    BehaviorExtractor,
)

from cogniverse_framework.analysis.behavior_explanation import (
    explain_behavior,
)


trajectory = Trajectory()

trajectory.add(
    Transition(
        "cb148158",
        "continue_branch",
        "success",
    )
)

trajectory.add(
    Transition(
        "790ffc07",
        "continue_branch",
        "success",
    )
)

evidence = BehaviorExtractor().extract(
    trajectory
)

explanation = explain_behavior(
    evidence
)

print(json.dumps({
    "bundle": "13",
    "replay_learning": "PASS",
    "strategy":
        evidence["strategy"],
    "confidence":
        evidence["confidence"],
    "explanation":
        explanation["explanation"],
}, indent=2))
PY
