# Value and homeostasis contracts v1 (F2 foundation)

## Purpose

Phase F2 adds generic value, safety, and homeostasis **records** — not lab-specific weighting or environment dynamics. Scalar reward cannot silently populate survival or safety fields.

## Implemented components

| Component | Status |
| --- | --- |
| `ConstraintScope`, `HardConstraint`, `ConstraintViolation` | **Implemented** |
| `ValueVector`, `ValueEstimate` | **Implemented** |
| `NeedState`, `HomeostaticUpdate` | **Implemented** |
| `LegacyScalarRewardAdapter` | **Implemented** |
| Scientific validation | **Not yet tested scientifically** |

## Key separation rules

1. **Hard constraints** are evaluated before soft value — they are not compensatable dimensions.
2. **`ValueVector`** rejects a direct `survival` dimension — use `NeedState` for homeostatic deficits.
3. **`LegacyScalarRewardAdapter`** maps scalar reward to an explicit opaque dimension; it cannot target `survival`, `safety`, or `homeostasis`.

## Example

```python
from cogniverse_framework.cognition import (
    ConstraintScope,
    HardConstraint,
    LegacyScalarRewardAdapter,
    NeedState,
    ValueVector,
)

need = NeedState(
    need_id="need-energy",
    source_system="lab-homeostasis",
    logical_step=5,
    need_kind="energy",
    level_ppm=190_000,
    target_ppm=700_000,
    deficit_ppm=510_000,
    evidence_ids=("observation-1",),
)

constraint = HardConstraint(
    constraint_id="constraint-no-harm",
    source_system="lab-safety",
    logical_step=5,
    scopes=(ConstraintScope.USER, ConstraintScope.SELF),
)

adapter = LegacyScalarRewardAdapter(
    adapter_id="legacy-task-reward",
    source_system="lab-legacy",
    logical_step=5,
    target_dimension_id="task-progress",
)
value = adapter.to_value_vector(
    vector_id="value-step-5",
    scalar_reward_ppm=400_000,
)
```

## Exit gate (F2)

- Deterministic serialization and digests
- Configuration/version provenance on all records
- Scalar reward cannot silently populate survival/safety
- Controlled lab mechanism plus ablation (pending)
- Second domain uses unchanged contracts (pending)

See [COGNITIVE_ARCHITECTURE_ROADMAP.md](COGNITIVE_ARCHITECTURE_ROADMAP.md) Phase F2.
