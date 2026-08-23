"""Thin EXP-042 contract demo.

Hardcoded experiment science (seeds, mutation timings, claim strings) belongs
in the learning lab. Pass them in via constructor arguments when exercising
this adapter as a fixture.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from cogniverse_framework.experiments.base_adapter import ExperimentAdapter
from cogniverse_framework.replay.compare import compare_seed_matrix
from cogniverse_framework.research import ReplaySession


class Exp042Adapter(ExperimentAdapter):
    """Framework-side demo of the experiment adapter contract."""

    experiment_id = "exp042"

    def __init__(
        self,
        replay_events: Sequence[Mapping[str, Any]] | None = None,
        *,
        seed: int = 0,
        baseline_scores: Mapping[Any, Any] | None = None,
        candidate_scores: Mapping[Any, Any] | None = None,
        learning_evidence: Mapping[str, Any] | None = None,
    ):
        self.replay_events = list(replay_events or [])
        self.seed = seed
        self.baseline_scores = dict(baseline_scores or {})
        self.candidate_scores = dict(candidate_scores or {})
        self._learning_evidence = dict(learning_evidence or {})

    def run(self):
        replay = ReplaySession(
            seed=self.seed,
            events=self.replay_events,
        )
        contract = replay.validate_replay_only()
        mutation = compare_seed_matrix(
            self.baseline_scores,
            self.candidate_scores,
        )

        return {
            "experiment": self.experiment_id,
            "status": "COMPLETE",
            "contract": contract,
            "mutation_analysis": mutation.to_dict(),
            "learning_evidence": dict(self._learning_evidence),
        }

    def execute(self):
        return self.run()

    def analyze(self, result):
        return result

    def collect_learning_evidence(self, result):
        return result.get("learning_evidence", {})
