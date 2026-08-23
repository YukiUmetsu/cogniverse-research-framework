"""Experiment-facing adapters.

Thin contract demos and wrappers. Hardcoded science stays in the learning lab.
"""

from .exp042 import Exp042Replay

__all__ = ["Exp042Replay"]
