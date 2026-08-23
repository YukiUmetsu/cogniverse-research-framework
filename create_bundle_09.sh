#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/integration \
  src/cogniverse_framework/experiments \
  src/cogniverse_framework/cli \
  tests \
  scripts

cat > src/cogniverse_framework/integration/__init__.py <<'PY'
from .experiment_runner import ExperimentRunner

__all__ = [
    "ExperimentRunner",
]
PY

cat > src/cogniverse_framework/integration/experiment_runner.py <<'PY'
from pathlib import Path
import json

from cogniverse_framework.execution.engine import (
    ExecutionEngine,
)

from cogniverse_framework.experiments.exp042 import (
    Exp042Adapter,
)

from cogniverse_framework.artifacts.manifest import (
    create_artifact_manifest,
)


class ExperimentRunner:

    ADAPTERS = {
        "exp042": Exp042Adapter,
    }

    def __init__(self, experiment_id):
        self.experiment_id = experiment_id

    def run(self, artifact_directory):

        if self.experiment_id not in self.ADAPTERS:
            raise ValueError(
                f"Unknown experiment: {self.experiment_id}"
            )

        adapter = self.ADAPTERS[
            self.experiment_id
        ]()

        result = ExecutionEngine(
            adapter
        ).run()

        artifact_path = Path(
            artifact_directory
        )

        artifact_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        output = artifact_path / "result.json"

        output.write_text(
            json.dumps(
                result,
                indent=2,
                default=str,
            )
        )

        manifest = create_artifact_manifest(
            artifact_path
        )

        return {
            "experiment": self.experiment_id,
            "result": result,
            "artifact_manifest": manifest,
        }
PY


cat > src/cogniverse_framework/experiments/manifest.py <<'PY'
from dataclasses import dataclass


@dataclass
class ExperimentManifest:

    experiment_id: str
    adapter: str

    def validate(self):

        return {
            "valid": bool(
                self.experiment_id
                and self.adapter
            )
        }
PY


cat > src/cogniverse_framework/cli/run_generated.py <<'PY'
import argparse
import json

from cogniverse_framework.integration import (
    ExperimentRunner,
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "experiment_id"
    )

    parser.add_argument(
        "--artifacts",
        default=".runtime/experiment",
    )

    args = parser.parse_args()

    result = ExperimentRunner(
        args.experiment_id
    ).run(
        args.artifacts
    )

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
PY


cat > tests/test_bundle_09_integration.py <<'PY'
import tempfile
import unittest

from cogniverse_framework.integration import (
    ExperimentRunner,
)


class TestBundle09(unittest.TestCase):

    def test_exp042_full_execution(self):

        with tempfile.TemporaryDirectory() as tmp:

            result = ExperimentRunner(
                "exp042"
            ).run(tmp)

            self.assertEqual(
                result["experiment"],
                "exp042",
            )

            self.assertEqual(
                result["result"]["status"],
                "COMPLETE",
            )


if __name__ == "__main__":
    unittest.main()
PY


cat > scripts/run_bundle_09.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 09: GENERATED EXP-042 INTEGRATION"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

rm -rf .runtime/bundle09

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.integration import (
    ExperimentRunner,
)

result = ExperimentRunner(
    "exp042"
).run(
    ".runtime/bundle09"
)

print(json.dumps({
    "bundle": "09",
    "experiment": result["experiment"],
    "status": result["result"]["status"],
    "artifacts": len(
        result["artifact_manifest"]["files"]
    ),
}, indent=2))
PY
SH

chmod +x scripts/run_bundle_09.sh

git add .
git commit -m "Implement Bundle 09 EXP-042 integration pipeline"

echo "Bundle 09 created"
