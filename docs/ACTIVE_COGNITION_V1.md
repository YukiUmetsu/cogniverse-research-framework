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
| Operation-log replay with stable digest | **Implemented** |
| Redis / external activation stores | **Proposed** |
| `CognitiveEventBus` | **Proposed** |
| `CognitiveGap` / `InformationNeed` | **Proposed** |
| `RetrievalController` | **Proposed** |
| Episodic / semantic / procedural memory ports | **Proposed** |
| World model / prediction deltas | **Proposed** |
| Scientific validation of activation policy | **Not yet tested scientifically** |

## 3. Contract test results

| Metric | Result | Meaning |
| --- | ---: | --- |
| Active cognition focused tests | 11/11 PASS | Graph, runtime, replay, projection |
| Full framework tests | 63/63 PASS | No regression in existing packages |
| `CognitiveState` v1 digest | unchanged | `32c435fe…07f7` |
| Active cognition verifier digest | `e8ac96a6…c216` | Deterministic replay fixture |
| LLM dependency | 0 | Runtime works without language models |
| Redis dependency | 0 | In-memory reference backend only |

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

## 6. Limitations

- Activation uses transparent integer ppm math, not learned policies.
- Working-memory eviction ranks by current activation with deterministic tie-breaking.
- `to_cognitive_state()` maps working-memory items to episodic memory refs as a projection convenience; this does not claim episodic storage semantics are complete.
- Passing contract tests does **not** demonstrate biological or task-level cognitive benefit.
- Learning Lab consumer equivalence (CA-I1 style) for active cognition is still **proposed**.

## 7. What is next

1. Pin framework commit in Learning Lab and add a thin active-cognition consumer.
2. Add `CognitiveGap` and retrieval ports (F4 retrieval foundation).
3. Introduce `CognitiveEventBus` with in-memory backend before optional Redis.
4. Run controlled ablations on activation/spreading/capacity — only then label mechanisms **experimentally validated**.

See also: [Active Cognition Architecture Audit](ACTIVE_COGNITION_ARCHITECTURE_AUDIT.md).
