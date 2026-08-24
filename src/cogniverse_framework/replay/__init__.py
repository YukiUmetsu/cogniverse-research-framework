"""Replay package: trajectories, ancestry, divergence, and compare helpers.

Generic infrastructure for replay-only analysis. Experiment-specific seeds,
claim strings, and mutation timings belong in the learning lab — inject them
through adapters or call these helpers with your own data.
"""

from .ancestry import ancestry_path, first_reach_parents, shared_ancestry
from .compare import compare_runs, compare_seed_matrix
from .divergence import (
    audit_sequence_divergence,
    classify_transition_divergence,
    find_later,
    first_divergence,
    post_divergence_budget,
)
from .seed_diagnosis import (
    diagnose_seed_failures,
    label_if_metric_strictly_lower,
    label_if_milestone_absent_on_hard,
    profiles_from_metric_table,
)
from .seed_diagnosis_types import (
    MetricContrast,
    MilestoneContrast,
    SeedFailureDiagnosis,
    SeedProfile,
)
from .trajectory import Trajectory
from .transition import Transition
from .types import (
    DivergencePoint,
    DivergenceResult,
    FirstDivergence,
    LaterLookup,
    RunCompareResult,
    SeedMatrixResult,
    SeedRow,
    SharedAncestryResult,
)

__all__ = [
    "Trajectory",
    "Transition",
    "LaterLookup",
    "FirstDivergence",
    "DivergencePoint",
    "DivergenceResult",
    "SharedAncestryResult",
    "SeedRow",
    "SeedMatrixResult",
    "RunCompareResult",
    "SeedProfile",
    "MetricContrast",
    "MilestoneContrast",
    "SeedFailureDiagnosis",
    "compare_runs",
    "compare_seed_matrix",
    "diagnose_seed_failures",
    "profiles_from_metric_table",
    "label_if_metric_strictly_lower",
    "label_if_milestone_absent_on_hard",
    "shared_ancestry",
    "first_reach_parents",
    "ancestry_path",
    "first_divergence",
    "classify_transition_divergence",
    "find_later",
    "audit_sequence_divergence",
    "post_divergence_budget",
]
