# Active cognition ablations

## Purpose

Controlled ablations validate whether active cognition mechanisms affect task behavior. Passing framework contract tests is **not** sufficient for scientific claims.

## Preregistration template

Record before running lab studies:

| Field | Value |
| --- | --- |
| Hypothesis ID | |
| Baseline condition | Full coordinator (spreading + retrieval) |
| Ablation condition | See table below |
| Seeds | |
| Equivalence gate | CA-I1 legacy actions/events unchanged when coordinator disabled |
| Primary metric | |
| Evidence artifacts | `snapshot.digest()`, `cognitive_state.digest()`, `cognitive_event_trace` |

## Framework ablation switches

Use `ActiveCognitionAblationConfig` from `cogniverse_framework.cognition`:

| Switch | Effect |
| --- | --- |
| `spreading_enabled=False` | Zero spreading boost in activation policy |
| `retrieval_enabled=False` | Perceive only; skip gap-driven retrieval |
| `working_capacity=N` | Override WM capacity for capacity ablations |

```python
from cogniverse_framework.cognition import (
    ActiveCognitionAblationConfig,
    build_ablation_coordinator,
    run_ablated_cycle,
)

config = ActiveCognitionAblationConfig(
    ablation_id="no-retrieval-v1",
    retrieval_enabled=False,
)
coordinator = build_ablation_coordinator(
    activation_policy,
    retrieval_policy,
    config,
    working_capacity=8,
)
result = run_ablated_cycle(coordinator, percept, config)
```

## Suggested first ablations

1. **CA-I1 equivalence** — coordinator disabled vs enabled (Learning Lab)
2. **No retrieval** — `retrieval_enabled=False`
3. **No spreading** — `spreading_enabled=False`
4. **Small WM** — `working_capacity=1` vs baseline capacity
5. **Redis event bus** — compare in-memory vs Redis backend traces

## Evidence recording

```python
from cogniverse_framework.replay import build_event_trace, event_trace_to_evidence_payload

trace = build_event_trace(coordinator.replay_events(), source_system="lab-consumer")
payload = event_trace_to_evidence_payload(trace)
# Store payload in lab evidence alongside snapshot and cognitive_state digests
```

## Status

| Item | Status |
| --- | --- |
| Framework ablation helpers | **Implemented** |
| Framework ablation tests | **Implemented** |
| Lab preregistered studies | **Pending** |
| Mechanisms labeled experimentally validated | **Not claimed** |
