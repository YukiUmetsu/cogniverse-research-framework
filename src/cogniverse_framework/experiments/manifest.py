from dataclasses import dataclass


@dataclass
class ExperimentManifest:
    experiment_id: str
    name: str
    mode: str
    environment: str
