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
