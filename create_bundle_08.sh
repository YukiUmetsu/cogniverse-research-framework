#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/research \
  src/cogniverse_framework/experiments/exp042 \
  src/cogniverse_framework/reporting \
  tests \
  scripts

cat > src/cogniverse_framework/research/__init__.py <<'PY'
from .replay_session import ReplaySession
from .mutation_analysis import MutationAnalysis

__all__ = [
    "ReplaySession",
    "MutationAnalysis",
]
PY

cat > src/cogniverse_framework/research/replay_session.py <<'PY'
from dataclasses import dataclass


@dataclass
class ReplaySession:

    seed: int
    events: list

    def validate_replay_only(self):

        violations = []

        for event in self.events:
            if event.get("reset_called"):
                violations.append(
                    "environment_reset"
                )

            if event.get("step_called"):
                violations.append(
                    "environment_step"
                )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def event_count(self):
        return len(self.events)
PY

cat > src/cogniverse_framework/research/mutation_analysis.py <<'PY'
from dataclasses import dataclass


@dataclass
class MutationAnalysis:

    baseline: dict
    candidate: dict

    def compare(self):

        changed = []

        for seed in sorted(
            set(self.baseline)
            | set(self.candidate)
        ):
            if (
                self.baseline.get(seed)
                != self.candidate.get(seed)
            ):
                changed.append(seed)

        return {
            "changed_seeds": changed,
            "changed_count": len(changed),
        }
PY

cat > src/cogniverse_framework/experiments/exp042/__init__.py <<'PY'
from .adapter import Exp042Adapter

__all__ = [
    "Exp042Adapter",
]
PY

cat > src/cogniverse_framework/experiments/exp042/adapter.py <<'PY'
from cogniverse_framework.research import (
    ReplaySession,
    MutationAnalysis,
)


class Exp042Adapter:

    experiment_id = "exp042"

    def __init__(self, replay_events=None):
        self.replay_events = replay_events or []

    def run(self):

        replay = ReplaySession(
            seed=51005,
            events=self.replay_events,
        )

        contract = (
            replay.validate_replay_only()
        )

        mutation = MutationAnalysis(
            baseline={
                51003: 376,
                51004: 305,
            },
            candidate={
                51003: 382,
                51004: 311,
            },
        ).compare()

        return {
            "experiment": self.experiment_id,
            "contract": contract,
            "mutation_analysis": mutation,
        }
PY

cat > src/cogniverse_framework/reporting/research_report.py <<'PY'
import json
from pathlib import Path


def write_research_report(path, result):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            result,
            indent=2,
        )
    )

    return str(path)
PY

cat > tests/test_bundle_08_exp042.py <<'PY'
import unittest

from cogniverse_framework.experiments.exp042 import (
    Exp042Adapter,
)


class TestBundle08(unittest.TestCase):

    def test_exp042_replay_contract(self):

        result = Exp042Adapter(
            [
                {
                    "observation": "state"
                }
            ]
        ).run()

        self.assertTrue(
            result["contract"]["valid"]
        )

    def test_mutation_analysis(self):

        result = Exp042Adapter().run()

        self.assertEqual(
            result["mutation_analysis"]
            ["changed_count"],
            2,
        )


if __name__ == "__main__":
    unittest.main()
PY

cat > scripts/run_bundle_08.sh <<'SH'
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
SH

chmod +x scripts/run_bundle_08.sh

git add .
git commit -m "Implement Bundle 08 EXP-042 migration adapter"

echo "Bundle 08 created"
