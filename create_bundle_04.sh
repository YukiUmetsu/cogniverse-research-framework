#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/adapters \
  src/cogniverse_framework/replay \
  src/cogniverse_framework/artifacts \
  src/cogniverse_framework/reporting \
  examples \
  scripts \
  tests

touch src/cogniverse_framework/adapters/__init__.py

cat > src/cogniverse_framework/experiments/yaml_loader.py <<'PY'
from pathlib import Path


def load_manifest(path):
    data = {}

    current = None

    for line in Path(path).read_text().splitlines():
        line = line.strip()

        if not line:
            continue

        if not line.startswith("-") and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if value:
                data[key] = value
            else:
                current = key
                data[current] = {}

    return data
PY

cat > src/cogniverse_framework/adapters/exp042.py <<'PY'
from dataclasses import dataclass


@dataclass
class Exp042Replay:
    name: str = "exp042"

    def classify(self, runtime):
        return {
            "experiment": self.name,
            "classification": (
                "REPLAY_ONLY"
                if runtime.get("minigrid_reset_or_step_called") is False
                else "ENVIRONMENT_EXECUTION"
            ),
        }

    def compare(self, baseline, candidate):
        changed = []

        seeds = set(baseline) | set(candidate)

        for seed in sorted(seeds):
            if baseline.get(seed) != candidate.get(seed):
                changed.append(seed)

        return {
            "changed_seeds": changed,
            "baseline_count": len(baseline),
            "candidate_count": len(candidate),
        }
PY

cat > src/cogniverse_framework/replay/seed_matrix.py <<'PY'
def compare_seed_matrix(baseline, candidate):
    rows = []

    for seed in sorted(
        set(baseline.keys()) | set(candidate.keys())
    ):
        rows.append({
            "seed": seed,
            "baseline": baseline.get(seed),
            "candidate": candidate.get(seed),
            "changed": (
                baseline.get(seed)
                != candidate.get(seed)
            ),
        })

    return rows
PY

cat > src/cogniverse_framework/replay/divergence.py <<'PY'
def first_divergence(left, right):
    length = min(len(left), len(right))

    for i in range(length):
        if left[i] != right[i]:
            return {
                "index": i,
                "left": left[i],
                "right": right[i],
            }

    if len(left) != len(right):
        return {
            "index": length,
            "type": "length_difference",
        }

    return None
PY

cat > src/cogniverse_framework/replay/ancestry.py <<'PY'
def shared_ancestry(left, right):
    shared = []

    for a, b in zip(left, right):
        if a != b:
            break
        shared.append(a)

    return {
        "shared_length": len(shared),
        "shared_states": shared,
    }
PY

cat > src/cogniverse_framework/artifacts/evidence.py <<'PY'
from pathlib import Path
import hashlib


class EvidenceRegistry:

    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def register(self, name, content):
        path = self.directory / name
        path.write_text(content)

        return {
            "file": str(path),
            "sha256": hashlib.sha256(
                path.read_bytes()
            ).hexdigest(),
        }
PY

cat > src/cogniverse_framework/reporting/experiment_summary.py <<'PY'
import json


def write_summary(path, result):
    with open(path, "w") as f:
        json.dump(
            result,
            f,
            indent=2,
        )
PY

cat > examples/exp042_replay.yaml <<'EOF'
experiment_id: exp042
name: replay-comparison

mode: replay
environment: minigrid

reset_forbidden: true
fresh_seed_forbidden: true
EOF

cat > tests/test_exp042_adapter.py <<'PY'
import unittest

from cogniverse_framework.adapters.exp042 import Exp042Replay


class TestExp042Adapter(unittest.TestCase):

    def test_replay_classification(self):
        result = Exp042Replay().classify({
            "minigrid_reset_or_step_called": False
        })

        self.assertEqual(
            result["classification"],
            "REPLAY_ONLY",
        )

    def test_seed_compare(self):
        result = Exp042Replay().compare(
            {1: "a"},
            {1: "b"},
        )

        self.assertEqual(
            result["changed_seeds"],
            [1],
        )


if __name__ == "__main__":
    unittest.main()
PY

cat > scripts/run_bundle_04.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 04: EXP-042 MIGRATION ADAPTER"

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python - <<'PY'
from cogniverse_framework.adapters.exp042 import Exp042Replay
from cogniverse_framework.replay.ancestry import shared_ancestry

print({
    "adapter": Exp042Replay().name,
    "classification": Exp042Replay().classify({
        "minigrid_reset_or_step_called": False
    }),
    "ancestry": shared_ancestry(
        ["a", "b", "c"],
        ["a", "b", "d"],
    ),
})
PY
SH

chmod +x scripts/run_bundle_04.sh

git add .
git commit -m "Add Bundle 04 EXP-042 migration adapter"

echo "Bundle 04 created"
