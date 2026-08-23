from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionResult:
    experiment_id: str
    status: str
    phase_results: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "experiment_id": self.experiment_id,
            "status": self.status,
            "phase_results": self.phase_results,
            "artifacts": self.artifacts,
        }
