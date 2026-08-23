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
