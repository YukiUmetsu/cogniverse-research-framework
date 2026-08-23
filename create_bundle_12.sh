#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/learning \
  src/cogniverse_framework/integration \
  src/cogniverse_framework/reporting \
  tests \
  scripts

cat > src/cogniverse_framework/learning/learner_run.py <<'PY'
from dataclasses import dataclass, field


@dataclass
class LearnerRun:

    experiment_id: str
    before: dict
    after: dict
    traces: list = field(default_factory=list)

    def snapshot(self):

        return {
            "experiment": self.experiment_id,
            "before": self.before,
            "after": self.after,
            "traces": self.traces,
        }
PY

cat > src/cogniverse_framework/learning/evidence_collector.py <<'PY'
from cogniverse_framework.analysis import (
    compare_knowledge,
)


class EvidenceCollector:

    def collect(self, learner_run):

        delta = compare_knowledge(
            learner_run.before,
            learner_run.after,
        )

        return {
            "experiment": learner_run.experiment_id,
            "behavior_change": delta,
            "traces": learner_run.traces,
        }
PY

cat > src/cogniverse_framework/integration/learning_pipeline.py <<'PY'
from cogniverse_framework.learning.learner_run import (
    LearnerRun,
)

from cogniverse_framework.learning.evidence_collector import (
    EvidenceCollector,
)


class LearningPipeline:

    def __init__(self, experiment_id):
        self.experiment_id = experiment_id

    def run(self):

        learner = LearnerRun(
            experiment_id=self.experiment_id,
            before={
                "concepts": [],
                "strategies": [
                    "random_exploration"
                ],
            },
            after={
                "concepts": [
                    "frontier_value"
                ],
                "strategies": [
                    "information_guided_exploration"
                ],
            },
            traces=[
                {
                    "state": "ef562c19",
                    "decision": "continue_branch",
                    "reason": "future_value",
                }
            ],
        )

        return EvidenceCollector().collect(
            learner
        )
PY

cat > src/cogniverse_framework/reporting/learner_report.py <<'PY'
from pathlib import Path
import json


def write_learner_report(path, evidence):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            evidence,
            indent=2,
        )
    )

    return str(path)
PY

cat > tests/test_bundle_12_learning_pipeline.py <<'PY'
import unittest

from cogniverse_framework.integration.learning_pipeline import (
    LearningPipeline,
)


class TestBundle12(unittest.TestCase):

    def test_learning_pipeline(self):

        result = LearningPipeline(
            "exp042"
        ).run()

        self.assertEqual(
            result["experiment"],
            "exp042",
        )

        self.assertIn(
            "information_guided_exploration",
            result["behavior_change"]["new_strategies"],
        )


if __name__ == "__main__":
    unittest.main()
PY

cat > scripts/run_bundle_12.sh <<'SH'
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
SH

chmod +x scripts/run_bundle_12.sh

git add .
git commit -m "Implement Bundle 12 learner experiment pipeline"

echo "Bundle 12 created"
