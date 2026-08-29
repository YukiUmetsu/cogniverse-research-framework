# Value and homeostasis contracts v1 (F2 foundation)

## Purpose

Phase F2 adds generic value, safety, and homeostasis **records and machinery** — not lab-specific weighting or environment dynamics. Scalar reward cannot silently populate survival or safety fields.

## Implemented components

| Component | Status |
| --- | --- |
| `ConstraintScope`, `HardConstraint`, `ConstraintViolation` | **Implemented** |
| `ConstraintEvaluation`, `evaluate_hard_constraints()` | **Implemented** |
| `ValueVector`, `ValueEstimate` | **Implemented** |
| `NeedState`, `HomeostaticUpdate` | **Implemented** |
| `TransparentPriorityPolicy`, `rank_need_states()` | **Implemented** |
| `LegacyScalarRewardAdapter` | **Implemented** |
| `ValueHomeostasisTrace` + evidence payload helpers | **Implemented** |
| F2 contract verifier | **Implemented** — digest `4eba925f…6aef` |
| Scientific validation | **Pending** (Learning Lab) |

## Key separation rules

1. **Hard constraints** are evaluated before soft value — they are not compensatable dimensions.
2. **`ValueVector`** rejects a direct `survival` dimension — use `NeedState` for homeostatic deficits.
3. **`LegacyScalarRewardAdapter`** maps scalar reward to an explicit opaque dimension; it cannot target `survival`, `safety`, or `homeostasis`.

## Constraint evaluation

```python
from cogniverse_framework.cognition import (
    ConstraintScope,
    HardConstraint,
    evaluate_hard_constraints,
)

constraint = HardConstraint(
    constraint_id="constraint-no-harm",
    source_system="lab-safety",
    logical_step=5,
    scopes=(ConstraintScope.USER, ConstraintScope.SELF),
    blocked_subject_ids=("action-harm",),
)

allowed = evaluate_hard_constraints(
    (constraint,),
    subject_id="action-safe",
    logical_step=5,
    source_system="lab-safety",
)
blocked = evaluate_hard_constraints(
    (constraint,),
    subject_id="action-harm",
    logical_step=5,
    source_system="lab-safety",
)
```

## Priority policy (reference)

```python
from cogniverse_framework.cognition import NeedState, TransparentPriorityPolicy, rank_need_states

policy = TransparentPriorityPolicy(
    policy_id="lab-priority",
    source_system="lab-homeostasis",
    need_kind_weights_ppm=(("energy", 800_000),),
)
ranked = rank_need_states((need,), policy)
```

## Evidence traces

```python
from cogniverse_framework.replay import (
    build_value_homeostasis_trace,
    value_homeostasis_trace_to_evidence_payload,
)

trace = build_value_homeostasis_trace(
    source_system="lab-ca-vh1",
    logical_step=5,
    need_states=(need,),
    constraint_evaluations=(allowed, blocked),
    ranked_needs=ranked,
)
payload = value_homeostasis_trace_to_evidence_payload(trace)
```

Verifier:

```bash
PYTHONPATH=src python scripts/verify_value_homeostasis_contract.py
```

## Exit gate (F2)

| Gate | Status |
| --- | --- |
| Deterministic serialization and digests | **Complete** |
| Constraint evaluation before soft value | **Complete** |
| Scalar reward isolation | **Complete** |
| F2 contract verifier | **Complete** |
| Lab mechanism + ablation | **Pending** |
| Second domain unchanged contracts | **Pending** |

See [COGNITIVE_ARCHITECTURE_ROADMAP.md](COGNITIVE_ARCHITECTURE_ROADMAP.md) Phase F2. Lab preregistration and experiment evidence belong in the Learning Lab repository.
