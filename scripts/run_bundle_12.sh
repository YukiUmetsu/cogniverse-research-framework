#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 12: LEARNER EXPERIMENT PIPELINE"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

rm -rf .runtime/bundle12

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.integration.learning_pipeline import (
    LearningPipeline,
)

from cogniverse_framework.reporting.learner_report import (
    write_learner_report,
)

result = LearningPipeline(
    "exp042"
).run()

report = write_learner_report(
    ".runtime/bundle12/learner_report.json",
    result,
)

print(json.dumps({
    "bundle": "12",
    "learning_pipeline": "PASS",
    "experiment": result["experiment"],
    "new_strategies":
        result["behavior_change"]["new_strategies"],
    "report": report,
}, indent=2))
PY
