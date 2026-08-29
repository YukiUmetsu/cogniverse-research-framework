# Active Cognition v1 foundation

## Status legend

| Label | Meaning |
| --- | --- |
| **Implemented** | Code and tests exist in this framework release |
| **Proposed** | Documented target, not yet coded |
| **Experimentally validated** | Used in a controlled Learning Lab study with preregistered outcomes |
| **Not yet tested scientifically** | Contract tests only |

## 1. Background

Cogniverse cognition is moving from a linear pipeline mental model toward **dynamic active cognition**: a small relational graph, bounded working memory, primed candidates, and deterministic activation that can be snapshotted into the existing `CognitiveState` v1 contract.

`CognitiveState` remains an immutable auditable snapshot. It is **not** mutable working memory.

## 2. What is implemented (F1.5 milestone)

| Component | Status |
| --- | --- |
| `ActiveCognitiveGraph`, typed nodes/edges | **Implemented** |
| `WorkingMemory` with capacity admission/eviction | **Implemented** |
| `PrimedMemory` ladder | **Implemented** |
| `ActivationPolicy` / `ActivationRecord` | **Implemented** |
| `InMemoryActiveCognitionRuntime` | **Implemented** |
| `ActiveCognitionSnapshot` → `CognitiveState` projection | **Implemented** |
| `ActivePerceptionConsumer` (`PublicPercept` bridge) | **Implemented** |
| `CognitiveGap` / `InformationNeed` | **Implemented** |
| `RetrievalRequest` / `RetrievalResult` / controller | **Implemented** |
| Memory role ports + in-memory stores | **Implemented** |
| Operation-log replay with stable digest | **Implemented** |
| `ActiveCognitionCoordinator` (full perceive → retrieve → feedback) | **Implemented** |
| Pluggable memory / event / activation backends (in-memory + optional Redis) | **Implemented** |
| Retrieval → WM/primed feedback loop | **Implemented** |
| Redis / external activation stores | **Implemented** (optional dependency) |
| `CognitiveEventBus` | **Implemented** (in-memory + optional Redis) |
| Framework reference coordinator fixture | **Implemented** |
| World model / prediction deltas | **Proposed** |
| Lab consumer equivalence (CA-I1 style) | **Complete** (Learning Lab — CA-I1/CA-P1) |
| Scientific validation of activation policy | **Not yet tested scientifically** |

## 3. Contract test results

| Metric | Result | Meaning |
| --- | ---: | --- |
| Active cognition focused tests | 11/11 PASS | Graph, runtime, replay, projection |
| Active perception bridge tests | 7/7 PASS | PublicPercept → runtime → CognitiveState |
| Cognition backends + coordinator tests | 6/6 PASS | Backends, coordinator, event replay |
| Full framework tests | 96/96 PASS | No regression in existing packages |
| `CognitiveState` v1 digest | unchanged | `32c435fe…07f7` |
| Active cognition verifier digest | `e8ac96a6…c216` | Deterministic replay fixture |
| Perception pipeline verifier digest | `84acaf19…e8bf` | PublicPercept bridge fixture |
| Coordinator verifier digest | `fa2343fe…ef160` | Full perceive → retrieve → feedback |
| LLM dependency | 0 | Runtime works without language models |
| Redis dependency | 0 (optional) | In-memory default; Redis via `[redis]` extra |

## 4. Architecture relationships

```text
Live runtime (implemented)
    InMemoryActiveCognitionRuntime
        ActiveCognitiveGraph
        WorkingMemory
        PrimedMemory
        ActivationPolicy (injected)
              |
              | snapshot()
              v
    ActiveCognitionSnapshot
              |
              | to_cognitive_state()
              v
    CognitiveState v1 (unchanged schema)
```

## 5. Example

### Direct active runtime

```python
from cogniverse_framework.cognition import (
    ActivationPolicy,
    ActiveCognitiveNode,
    InMemoryActiveCognitionRuntime,
    NodeCategory,
)

policy = ActivationPolicy(
    policy_id="lab-injected-policy",
    decay_ppm=900_000,
    perception_boost_ppm=500_000,
    spreading_boost_ppm=150_000,
    working_threshold_ppm=300_000,
    primed_threshold_ppm=100_000,
)

runtime = InMemoryActiveCognitionRuntime(policy, working_capacity=4)
runtime.add_perceived_node(
    ActiveCognitiveNode(
        node_id="entity-1",
        category=NodeCategory.ENTITY,
        source_system="public-perception",
        logical_step=1,
        evidence_ids=("event-1",),
    )
)
snapshot = runtime.snapshot()
state = snapshot.to_cognitive_state(state_id="step-1")
```

### PublicPercept bridge (recommended lab integration surface)

```python
from cogniverse_framework.cognition import (
    ActivationPolicy,
    ActivePerceptionConsumer,
    PublicPercept,
)

policy = ActivationPolicy(
    policy_id="lab-injected-policy",
    decay_ppm=900_000,
    perception_boost_ppm=500_000,
    spreading_boost_ppm=150_000,
    working_threshold_ppm=300_000,
    primed_threshold_ppm=100_000,
)

consumer = ActivePerceptionConsumer(policy, working_capacity=4)

# Lab adapter builds PublicPercept from environment-native observations.
percept = PublicPercept(...)  # from lab adapter
step = consumer.receive(percept)
state = step.cognitive_state
```

For batch replay in tests, use `ActivePerceptionConsumer.process_percepts(...)`.

## 6. Limitations

- Activation uses transparent integer ppm math, not learned policies.
- Working-memory eviction ranks by current activation with deterministic tie-breaking.
- `to_cognitive_state()` maps working-memory items to episodic memory refs as a projection convenience; this does not claim episodic storage semantics are complete.
- Passing contract tests does **not** demonstrate biological or task-level cognitive benefit.
- Lab CA-I1/CA-P1 consumer equivalence (CA-I1 style) for active cognition is **complete** — see [LAB_ACTIVE_COGNITION_INTEGRATION.md](LAB_ACTIVE_COGNITION_INTEGRATION.md).

## 7. Learning Lab integration checklist

The framework cannot import the lab. Use [LAB_ACTIVE_COGNITION_INTEGRATION.md](LAB_ACTIVE_COGNITION_INTEGRATION.md) and the reference fixture in `tests/test_coordinator_fixture.py`.

Recommended surface: `ActiveCognitionCoordinator` with lab-injected policies and pluggable backends.

Verifiers:

```bash
PYTHONPATH=src python scripts/verify_active_perception_pipeline.py
PYTHONPATH=src python scripts/verify_active_cognition_coordinator.py
```

## 8. What is next

1. Learning Lab: advance framework pin, re-run equivalence gates, and run value/homeostasis mechanism studies using F2 APIs — see [VALUE_HOMEOSTASIS_V1.md](VALUE_HOMEOSTASIS_V1.md).
2. Optional PostgreSQL/graph/vector memory backends behind the same ports.
3. Phase F3 world-model contracts after F2 lab validation.
4. Run controlled ablations — only then label mechanisms **experimentally validated**.

See [Cognition backends v1](COGNITION_BACKENDS_V1.md), [Retrieval foundation v1](RETRIEVAL_FOUNDATION_V1.md), and [Active cognition ablations](ACTIVE_COGNITION_ABLATIONS.md).

See also: [Active Cognition Architecture Audit](ACTIVE_COGNITION_ARCHITECTURE_AUDIT.md).
