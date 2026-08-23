"""Compatibility shim — prefer ``replay.compare.compare_runs``."""

from .compare import compare_runs

__all__ = ["compare_runs"]
