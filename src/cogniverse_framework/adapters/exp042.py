"""EXP-042 replay helpers as thin wrappers over the generic compare API.

Classification and seed diffs are framework infrastructure. Seed values and
claim labels remain the learning lab's responsibility.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cogniverse_framework.replay.compare import compare_seed_matrix


@dataclass
class Exp042Replay:
    name: str = "exp042"

    def classify(self, runtime: Mapping[str, Any]) -> dict[str, str]:
        replay_only = runtime.get("minigrid_reset_or_step_called") is False
        return {
            "experiment": self.name,
            "classification": (
                "REPLAY_ONLY" if replay_only else "ENVIRONMENT_EXECUTION"
            ),
        }

    def compare(
        self,
        baseline: Mapping[Any, Any],
        candidate: Mapping[Any, Any],
    ) -> dict[str, Any]:
        result = compare_seed_matrix(baseline, candidate)
        return {
            "changed_seeds": result.changed_seeds,
            "baseline_count": len(baseline),
            "candidate_count": len(candidate),
        }
