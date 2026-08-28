# Learning Lab — Active Cognition Integration

This guide is for the **Learning Lab** repository. The framework cannot import the lab; implement the steps below in the lab after pinning a framework commit that includes `ActiveCognitionCoordinator`.

## 1. Pin framework commit

Record the exact framework commit or release in lab dependency metadata. Required symbols:

- `ActiveCognitionCoordinator`
- `ActivationPolicy`, `RetrievalRankingPolicy`
- `PublicPercept`
- `build_event_trace`, `event_trace_to_evidence_payload` (from `cogniverse_framework.replay`)

## 2. Thin environment adapter

Keep environment decoding in the lab. Output `PublicPercept` only:

```python
from cogniverse_framework.cognition import PerceptModality, PublicPercept

def environment_observation_to_public_percept(observation, *, logical_step: int) -> PublicPercept:
    ...
```

See the reference fixture: [`tests/test_coordinator_fixture.py`](../tests/test_coordinator_fixture.py).

## 3. Instantiate coordinator with lab-injected policies

```python
from cogniverse_framework.cognition import (
    ActiveCognitionCoordinator,
    ActivationPolicy,
    NodeCategory,
    RetrievalRankingPolicy,
    episodic_memory_record,
)

coordinator = ActiveCognitionCoordinator(
    activation_policy,      # from experiment config
    retrieval_policy,       # from experiment config
    working_capacity=8,
    memory_backend="inmemory",  # or "redis" with redis_client=
    event_backend="inmemory",
    node_category=NodeCategory.EVENT,
    source_system="lab-active-cognition-consumer",
)
```

## 4. Per-step loop

```python
from cogniverse_framework.replay import build_event_trace, event_trace_to_evidence_payload

result = coordinator.receive_and_retrieve(
    public_percept,
    goal_node_ids=active_goal_node_ids,
)
cognitive_state = result.cognitive_state
snapshot_digest = result.snapshot.digest()
state_digest = result.cognitive_state.digest()

trace = build_event_trace(
    coordinator.replay_events(),
    source_system="lab-active-cognition-consumer",
)
evidence_payload = event_trace_to_evidence_payload(trace)
```

Store `snapshot_digest`, `state_digest`, and `evidence_payload` in lab evidence for replay audit.

## 5. CA-I1 equivalence (preregister)

Preregister exact legacy equivalence:

| Condition | Expected |
| --- | --- |
| Coordinator **disabled** | Legacy actions, events, evidence unchanged |
| Coordinator **enabled** | Same legacy outputs; plus optional cognitive digests in evidence |

Run both conditions on the same seeds and compare with existing replay helpers.

## 6. Optional Redis backends

```bash
pip install "cogniverse-research-framework[redis]"
```

```python
import redis

client = redis.Redis(host="127.0.0.1", port=6379, db=0)
coordinator = ActiveCognitionCoordinator(
    activation_policy,
    retrieval_policy,
    working_capacity=8,
    memory_backend="redis",
    event_backend="redis",
    redis_client=client,
)
```

## 7. Verifiers (framework-side)

Run before pinning:

```bash
PYTHONPATH=src python scripts/verify_active_cognition_coordinator.py
PYTHONPATH=src python scripts/verify_active_perception_pipeline.py
PYTHONPATH=src python scripts/verify_retrieval_foundation.py
```

## 8. Ablation studies

Use framework ablation helpers after baseline equivalence is proven. See [ACTIVE_COGNITION_ABLATIONS.md](ACTIVE_COGNITION_ABLATIONS.md).

## Status

| Item | Owner | Status |
| --- | --- | --- |
| Framework reference fixture | Framework | Complete |
| Lab consumer wiring | Learning Lab | Pending |
| CA-I1 equivalence study | Learning Lab | Pending |
| Evidence digests in lab runs | Learning Lab | Pending |
