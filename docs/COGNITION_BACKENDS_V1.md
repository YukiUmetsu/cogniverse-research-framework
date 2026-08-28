# Cognition backends v1

## Purpose

Active cognition storage and transport are **pluggable**. Redis (or any future backend) is an implementation detail — not the cognitive theory. Framework tests run without Redis.

## Ports

| Port | Responsibility |
| --- | --- |
| `MemoryStorePort` / `MemoryStoreSetPort` | Episodic, semantic, procedural long-term memory |
| `ActivationStorePort` | Optional node activation persistence |
| `CognitiveEventBusPort` | Typed runtime events (`PERCEPT_RECEIVED`, `MEMORY_RETRIEVED`, …) |

## Implementations

| Backend | Memory | Events | Activation |
| --- | --- | --- | --- |
| `inmemory` | **Implemented** | **Implemented** | **Implemented** |
| `redis` | **Implemented** (optional) | **Implemented** (optional) | **Implemented** (optional) |

Install Redis support in consumers:

```bash
pip install "cogniverse-research-framework[redis]"
```

## Factory (swap backends)

```python
from cogniverse_framework.cognition import (
    create_memory_store_set,
    create_event_bus,
    create_activation_store,
)

memory = create_memory_store_set("inmemory")
bus = create_event_bus("inmemory")
activation = create_activation_store("inmemory")

# Later, swap without changing cognitive contracts:
# memory = create_memory_store_set("redis", redis_client=client)
# bus = create_event_bus("redis", redis_client=client)
```

Inject custom clients when testing or running against a specific Redis instance:

```python
import redis

client = redis.Redis(host="127.0.0.1", port=6379, db=0)
memory = create_memory_store_set("redis", redis_client=client)
```

## Coordinator (full loop)

`ActiveCognitionCoordinator` wires perception → active runtime → gap-driven retrieval → memory feedback → event publication:

```python
from cogniverse_framework.cognition import (
    ActiveCognitionCoordinator,
    ActivationPolicy,
    RetrievalRankingPolicy,
    episodic_memory_record,
    event_percept,  # your lab adapter builds PublicPercept
)

coordinator = ActiveCognitionCoordinator(
    activation_policy,
    retrieval_policy,
    working_capacity=8,
    memory_backend="inmemory",
    event_backend="inmemory",
    node_category=NodeCategory.EVENT,
)

coordinator.store_memory(episodic_memory_record(...))
result = coordinator.receive_and_retrieve(percept)
events = coordinator.replay_events()
state = result.cognitive_state
```

## Retrieval feedback

Retrieved candidates are materialized into the active graph via `apply_retrieval_result()` / `runtime.admit_retrieved_node()`, then working/primed layers refresh automatically.

## Status

| Item | Status |
| --- | --- |
| Port contracts | **Implemented** |
| In-memory backends | **Implemented** |
| Redis backends | **Implemented** (optional dependency) |
| Coordinator | **Implemented** |
| Scientific validation | **Not yet tested scientifically** |

## Limitations

- Redis backends serialize records/events as JSON; schema migration is consumer responsibility.
- The coordinator owns the in-process active runtime; distributed runtime sync is future work.
- Passing contract tests does not prove Redis or retrieval improves task performance.
