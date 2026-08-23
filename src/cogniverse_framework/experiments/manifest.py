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
