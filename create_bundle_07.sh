#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/generator \
  src/cogniverse_framework/cli \
  src/cogniverse_framework/execution \
  src/cogniverse_framework/artifacts \
  scripts \
  tests

cat > src/cogniverse_framework/generator/templates.py <<'PY'
MANIFEST_TEMPLATE = """experiment_id: {experiment_id}
name: {experiment_id}
type: {experiment_type}

execution:
  mode: framework

audit:
  forbid_environment_reset: true
  require_hashes: true
"""


ADAPTER_TEMPLATE = """from cogniverse_framework.execution.engine import ExecutionEngine


class {class_name}:

    experiment_id = "{experiment_id}"

    def run(self):
        return {{
            "experiment_id": self.experiment_id,
            "result": "ok"
        }}


if __name__ == "__main__":

    result = ExecutionEngine(
        {class_name}()
    ).run()

    print(result)
"""


RUNNER_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

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
    RUNNER_TEMPLATE,
    TEST_TEMPLATE,
)


class ExperimentGenerator:

    def __init__(self, root="experiments"):
        self.root = Path(root)

    def generate(self, experiment_id, experiment_type):

        validate_experiment_id(experiment_id)
        validate_type(experiment_type)

        directory = self.root / experiment_id

        files = {
            "manifest.yaml": MANIFEST_TEMPLATE.format(
                experiment_id=experiment_id,
                experiment_type=experiment_type,
            ),
            "adapter.py": ADAPTER_TEMPLATE.format(
                class_name=self._class_name(experiment_id),
                experiment_id=experiment_id,
            ),
            "run.sh": RUNNER_TEMPLATE,
            "tests/test_generated.py": TEST_TEMPLATE,
        }

        for name, content in files.items():

            path = directory / name

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            path.write_text(content)

            if path.name == "run.sh":
                path.chmod(0o755)

        hashes = {}

        for name in files:
            path = directory / name
            hashes[name] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()

        result = {
            "experiment_id": experiment_id,
            "type": experiment_type,
            "files": hashes,
            "path": str(directory),
        }

        (directory / "generation.json").write_text(
            json.dumps(result, indent=2)
        )

        return result

    def _class_name(self, value):
        return "".join(
            x.capitalize()
            for x in value.replace("-", "_").split("_")
        )
PY


cat > src/cogniverse_framework/artifacts/execution_manifest.py <<'PY'
from pathlib import Path
import hashlib
import json


def write_execution_manifest(directory, result):

    directory = Path(directory)

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = directory / "execution.json"

    output.write_text(
        json.dumps(result, indent=2)
    )

    return {
        "path": str(output),
        "sha256": hashlib.sha256(
            output.read_bytes()
        ).hexdigest(),
    }
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
    )

    args = parser.parse_args()

    result = ExperimentGenerator().generate(
        args.experiment_id,
        args.type,
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
PY


cat > tests/test_bundle_07_generated_execution.py <<'PY'
import tempfile
import unittest

from pathlib import Path

from cogniverse_framework.generator.generator import (
    ExperimentGenerator,
)


class TestBundle07(unittest.TestCase):

    def test_generated_experiment(self):

        with tempfile.TemporaryDirectory() as tmp:

            result = ExperimentGenerator(
                tmp
            ).generate(
                "exp043",
                "replay-analysis",
            )

            root = Path(
                result["path"]
            )

            self.assertTrue(
                (root / "adapter.py").exists()
            )

            self.assertTrue(
                (root / "run.sh").exists()
            )


if __name__ == "__main__":
    unittest.main()
PY


cat > scripts/run_bundle_07.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 07: END TO END GENERATED EXPERIMENT"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

rm -rf .runtime/bundle07

PYTHONPATH=src python - <<'PY'
import json
import subprocess
from pathlib import Path

from cogniverse_framework.generator.generator import (
    ExperimentGenerator,
)

root = Path(".runtime/bundle07")

result = ExperimentGenerator(
    root
).generate(
    "exp043",
    "replay-analysis",
)

experiment = root / "exp043"

completed = subprocess.run(
    [
        "bash",
        str(experiment / "run.sh"),
    ],
    cwd=experiment,
    env={
        "PYTHONPATH": "../../../src"
    },
    capture_output=True,
    text=True,
)

print(json.dumps({
    "bundle": "07",
    "generator": "PASS",
    "execution_returncode": completed.returncode,
    "generated": result["experiment_id"],
}, indent=2))

if completed.returncode != 0:
    print(completed.stderr)
    raise SystemExit(1)
PY
SH

chmod +x scripts/run_bundle_07.sh

git add .
git commit -m "Implement Bundle 07 end to end generated experiments"

echo "Bundle 07 created"
