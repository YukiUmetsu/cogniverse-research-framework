#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/experiments \
  src/cogniverse_framework/contracts \
  src/cogniverse_framework/artifacts \
  src/cogniverse_framework/reporting \
  src/cogniverse_framework/replay \
  src/cogniverse_framework/plugins \
  tests \
  examples \
  docs

touch \
  src/cogniverse_framework/__init__.py \
  src/cogniverse_framework/experiments/__init__.py \
  src/cogniverse_framework/contracts/__init__.py \
  src/cogniverse_framework/artifacts/__init__.py \
  src/cogniverse_framework/reporting/__init__.py \
  src/cogniverse_framework/replay/__init__.py \
  src/cogniverse_framework/plugins/__init__.py

cat > pyproject.toml <<'EOF'
[project]
name = "cogniverse-research-framework"
version = "0.1.0"
requires-python = ">=3.10"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
pythonpath = ["src"]
EOF

cat > README.md <<'EOF'
# Cogniverse Research Framework

Reusable infrastructure for long-running AI research experiments.

Goals:
- reproducible experiment execution
- artifact management
- audit contracts
- replay analysis
- experiment bundles

Initial extraction target:
EXP-042 from cogniverse-learning-lab.
EOF

cat > src/cogniverse_framework/artifacts/hashing.py <<'EOF'
from hashlib import sha256
from pathlib import Path


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()
EOF

cat > src/cogniverse_framework/artifacts/manager.py <<'EOF'
from pathlib import Path
import json
from .hashing import sha256_file


class ArtifactManager:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, name: str, data: dict):
        path = self.output_dir / name
        path.write_text(json.dumps(data, indent=2, sort_keys=True))
        return {
            "path": str(path),
            "sha256": sha256_file(path),
        }
EOF

cat > src/cogniverse_framework/contracts/validator.py <<'EOF'
def validate_contract(contract: dict) -> dict:
    required = [
        "fresh_seed_block_opened",
        "heldout_seed_block_opened",
        "minigrid_reset_or_step_called",
    ]

    failures = [
        key for key in required
        if contract.get(key) is True
    ]

    return {
        "validated": len(failures) == 0,
        "failures": failures,
    }
EOF

cat > src/cogniverse_framework/experiments/manifest.py <<'EOF'
from dataclasses import dataclass


@dataclass
class ExperimentManifest:
    experiment_id: str
    name: str
    mode: str
    environment: str
EOF

cat > src/cogniverse_framework/reporting/summary.py <<'EOF'
def summarize(result: dict) -> dict:
    return {
        "status": result.get("status"),
        "experiment": result.get("experiment"),
    }
EOF

cat > examples/experiment.yaml <<'EOF'
experiment:
  id: exp000
  name: example
  mode: replay
  environment: minigrid

validation:
  require_clean_tree: true
  require_no_environment_reset: true
EOF

cat > docs/ARCHITECTURE.md <<'EOF'
# Architecture

Experiment lifecycle:

preflight
 -> execute
 -> analyze
 -> compare
 -> settle
 -> archive

The framework provides reusable infrastructure.
Research-specific logic remains in the experiment repository.
EOF

echo "Framework scaffold created."
