"""Research helpers built on replay infrastructure.

``ReplaySession`` validates replay-only contracts. ``MutationAnalysis`` is a
thin seed-matrix wrapper — prefer ``cogniverse_framework.replay.compare``.
"""

from .mutation_analysis import MutationAnalysis
from .replay_session import ReplaySession

__all__ = [
    "ReplaySession",
    "MutationAnalysis",
]
