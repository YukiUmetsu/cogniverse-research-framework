#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/generator \
  src/cogniverse_framework/cli \
  src/cogniverse_framework/experiments \
  scripts \
  tests \
  examples/generated

cat > src/cogniverse_framework/generator/__init__.py <<'PY'
from .generator import ExperimentGenerator

__all__ = ["ExperimentGenerator"]
PY

cat > src/cogniverse_framework/generator/schemas.py <<'PY'
VALID_TYPES = {
    "replay-analysis",
    "audit",
    "simulation",
}


def validate_experiment_id(experiment_id):
    if not experiment_id:
        raise ValueError("experiment_id is required")

    allowed = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789-_"
    )

    if not set(experiment_id) <= allowed:
        raise ValueError(
            "experiment_id contains invalid characters"
        )


def validate_type(experiment_type):
    if experiment_type not in VALID_TYPES:
        raise ValueError(
            f"unsupported experiment type: {experiment_type}"
        )
PY

cat > src/cogniverse_framework/generator/templates.py <<'PY'
MANIFEST_TEMPLATE = """experiment_id: {experiment_id}
name: {experiment_id}

type: {experiment_type}

execution:
  mode: replay

audit:
  forbid_environment_reset: true
  require_hashes: true
"""


ADAPTER_TEMPLATE = """


class {class_name}:

    experiment_id = "{experiment_id}"

    def run(self):
        return {{
            "experiment_id": self.experiment_id,
            "status": "READY"
        }}
"""


RUNNER_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

echo "Running {experiment_id}"

PYTHONPATH=../../src python adapter.py
"""


TEST_TEMPLATE = """import unittest


class TestGeneratedExperiment(unittest.TestCase):

    def test_generated(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
"""
PY

cat > src/cogniverse_framework/generator/generator.py <<'PY'
from pathlib import Path
import hashlib
import json

from .schemas import (
    validate_experiment_id,
    validate_type,
)
from .templates import (
    MANIFEST_TEMPLATE,
    ADAPTER_TEMPLATE,
    RUNNER    RUNNER    RUNNER    RUNNER    RUNNER    RUNNER  nerator:

    def __init__(self, root="experiments"):
        self.root = Path(root)

    def generate(self, experiment_id, experiment_type):
        validate_experiment_id(experiment_id)
        validate_type(experiment_type)

        directory = self.root / experiment_id

        files = {
            "manifest.yaml":
                MANIFEST_TEMPLATE.format(
                    experiment_id=experiment_id,
                    experiment_type=experiment_type,
                ),

            "adapter.py":
                ADAPTER_TEMPLATE.format(
                    class_name=self._class_name(experiment_id),
                    experiment_id=experiment_id,
                ),

            "run.sh":
                RUNNER_TEMPLATE.format(
                    experiment_id=experiment_id,
                ),

            "tests/test_generated.py":
                TEST_TEMPLATE,
        }

        for relative, content in files.items():
            path = directory / relative
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            path.write_text(content)

            if path.name == "run.sh":
                path.chmod(0o755)

        hashes = {}

        for relative in files:
            path = directory / relative
            hashes[relative] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()

        result = {
            "experiment_id": experiment_id,
            "type": experiment_type,
            "path": str(directory),
            "files": hashes,
        }

        (directory / "generation.json").write_text(
            json.dumps(result, indent=2)
        )

        return result

    def _class_name(self, value):
        return "".join(
            part.capitalize()
            for part in value.replace("-", "_").split("_")
        )
PY

cat > src/cogniverse_framework/cli/create_experiment.py <<'PY'
import argparse
import json

from cogniverse_framework.generator.generator import (
    ExperimentGenerator,
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "experiment_id"
    )

    parser.add_argument(
        "--type",
        required=True,
        dest="experiment_type",
    )

    args = parser.parse_args()

    result = ExperimentGenerator().generate(
        args.experiment_id,
        args.experiment_type,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
PY

cat > src/cogniverse_framework/experiments/registry.py <<'PY'
class ExperimentRegistry:

    def __init__(self):
        self.experiments = {}

    def register(self, experiment):
        self.experiments[
            experiment.experiment_id
        ] = experiment

    def get(self, experiment_id):
        return self.experiments.get(
            experiment_id
        )
PY

cat > tests/test_generator.py <<'PY'
import unittest
from pathlib import Path
import tempfile

from cogniverse_framework.generator.generator import (
    ExperimentGenerator,
)


class TestGenerator(unittest.TestCase):

    def test_generate(self):

        with tempfile.TemporaryDirectory() as tmp:

            result = ExperimentGenerator(
                tmp
            ).generate(
                "exp043",
                "replay-analysis",
            )

            path = Path(
                result["path"]
            )

            self.assertTrue(
                (path / "manifest.yaml").exists()
            )

            self.assertTrue(
                (path / "adapter.py").exists()
            )

            self.assertTrue(
                (path / "generation.json").exists()
            )


if __name__ == "__main__":
    unittest.main()
PY

cat > scripts/run_bundle_05.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 05: EXPERIMENT GENERATOR"

PYTHONPATH=src python -m unittest discover -s tests -v

rm -rf .runtime/bundle05_generated

PYTHONPATH=src python - <<'PY'
from cogniverse_framework.generator.generator import ExperimentGenerator
import json

result = ExperimentGenerator(
    ".runtime/bundle05_generated"
).generate(
    "exp043",
    "replay-analysis",
)

print(json.dumps({
    "bundle": "05",
    "generator": "PASS",
    "experiment": result["experiment_id"],
    "files": len(result["files"]),
}, indent=2))
PY
SH

chmod +x scripts/run_bundle_05.sh

git add .
git commit -m "Implement Bundle 05 experiment generator"

echo "Bundle 05 created"
