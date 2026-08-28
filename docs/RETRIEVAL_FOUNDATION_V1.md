# Retrieval foundation v1

## Status legend

| Label | Meaning |
| --- | --- |
| **Implemented** | Code and tests exist in this framework release |
| **Proposed** | Documented target, not yet coded |
| **Experimentally validated** | Used in a controlled Learning Lab study |
| **Not yet tested scientifically** | Contract tests only |

## 1. Purpose

Memory retrieval should be driven by **cognitive gaps and goals**, not surface similarity alone. This milestone adds typed gap detection, retrieval requests/results, transparent ranking, memory-role ports, and a reference in-memory controller.

## 2. Implemented components

| Component | Status |
| --- | --- |
| `CognitiveGap`, `InformationNeed` | **Implemented** |
| `RetrievalRequest`, `RetrievalResult`, `RetrievalCandidate` | **Implemented** |
| `RetrievalRankingPolicy` with transparent signals | **Implemented** |
| `LongTermMemoryRecord` (+ role factories) | **Implemented** |
| `EpisodicMemoryPort`, `SemanticMemoryPort`, `ProceduralMemoryPort` | **Implemented** (protocols) |
| `InMemoryMemoryStore` / `InMemoryMemoryStoreSet` | **Implemented** |
| `detect_cognitive_gaps` | **Implemented** |
| `InMemoryRetrievalController` | **Implemented** |
| Learned retrieval / vector backends | **Proposed** |
| Applying retrieval results back into activation/WM | **Implemented** |
| `CognitiveEventBus` in-memory + Redis optional | **Implemented** |
| Pluggable memory/activation/event backends | **Implemented** |
| Scientific validation | **Not yet tested scientifically** |

## 3. Contract test results

| Metric | Result |
| --- | ---: |
| Retrieval foundation tests | 5/5 PASS |
| Cognition backends + coordinator tests | 6/6 PASS |
| Full framework tests | 92/92 PASS |
| Retrieval verifier result digest | `188c6044…941a` |
| `CognitiveState` v1 digest | unchanged |

## 4. Architecture flow

```text
ActiveCognitionSnapshot
        |
        v
detect_cognitive_gaps()
        |
        v
InformationNeed (per gap)
        |
        v
RetrievalRequest (role + budget + context node ids)
        |
        v
InMemoryMemoryStoreSet.query + RetrievalRankingPolicy
        |
        v
RetrievalResult (ranked candidates with score components)
```

Retrieval uses:

- active graph digest;
- working and primed node ids;
- optional goal node ids;
- gap kind → default memory-role selection.

## 5. Example

```python
from cogniverse_framework.cognition import (
    ActivePerceptionConsumer,
    InMemoryRetrievalController,
    RetrievalRankingPolicy,
    episodic_memory_record,
)

consumer = ActivePerceptionConsumer(...)
snapshot = consumer.snapshot()

controller = InMemoryRetrievalController(ranking_policy)
controller.store(
    episodic_memory_record(
        memory_id="episode-1",
        source_system="lab-memory",
        logical_step=1,
        content_sha256="...",
        evidence_ids=("evidence-1",),
        related_node_ids=("percept.event-1",),
    )
)
session = controller.run_for_snapshot(snapshot)
top = session.results[0].candidates[0]
```

## 6. Gap detection rules (v1)

| Condition | Gap kind |
| --- | --- |
| `EVENT` node without incoming `POSSIBLE_CAUSE` | `unknown_cause` |
| Node `confidence_ppm` below threshold | `low_prediction_confidence` |
| `GOAL` node without outgoing `REQUIRES` | `unknown_goal_precondition` |
| `BELIEF` nodes linked by `CONTRADICTS` | `unresolved_belief_conflict` |

All thresholds are injected by callers/experiments.

## 7. Limitations

- Ranking is transparent integer ppm math, not learned.
- In-memory stores are reference backends only; Redis optional.
- Retrieval results are fed back via `apply_retrieval_result()` and `ActiveCognitionCoordinator`.
- Passing tests do not prove retrieval improves task performance.

## 8. What is next

1. Pin framework commit in Learning Lab and run `ActiveCognitionCoordinator` in one consumer loop.
2. Add PostgreSQL/graph/vector backends behind the same memory ports.
3. Run controlled ablations — only then label mechanisms **experimentally validated**.

See [Cognition backends v1](../COGNITION_BACKENDS_V1.md).

Verifier:

```bash
PYTHONPATH=src python scripts/verify_retrieval_foundation.py
```
