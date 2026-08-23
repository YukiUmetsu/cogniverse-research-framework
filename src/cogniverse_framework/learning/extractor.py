"""Derive strategy labels from replay trajectories.

Generic heuristics only. Experiment-specific claim names (e.g. lab strategy
ids) should be injected by the caller.
"""

from __future__ import annotations


class BehaviorExtractor:
    """Map successful trajectory actions to a strategy evidence blob."""

    def __init__(
        self,
        *,
        continue_branch_strategy: str = "continue_successful_branch",
    ):
        self.continue_branch_strategy = continue_branch_strategy

    def extract(self, trajectory):
        actions = trajectory.successful_actions()

        if "continue_branch" in actions:
            return {
                "strategy": self.continue_branch_strategy,
                "reason": "successful continuation after exploration",
                "evidence_states": trajectory.states(),
                "confidence": 0.74,
            }

        return {
            "strategy": "unknown",
            "reason": "insufficient evidence",
            "evidence_states": trajectory.states(),
            "confidence": 0.0,
        }
