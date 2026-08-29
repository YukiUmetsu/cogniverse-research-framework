# Active Cognition Architecture Audit

**Date:** 2026-08-27  
**Scope:** Pre-implementation audit for migrating toward dynamic active cognition  
**Status:** Engineering audit — not a scientific validation of cognitive mechanisms

---

## 1. Current architecture audit

### 1.1 Repository shape

The framework (`cogniverse_framework`) is organized as a research platform with thin cognitive contracts and substantial execution/evidence/replay machinery:

| Area | Location | Role today |
| --- | --- | --- |
| Cognitive contracts | `cognition/state.py`, `cognition/perception.py`, `cognition/_validation.py` | Immutable `CognitiveState`, `CognitiveReference`, `PublicPercept` |
| Execution lifecycle | `execution/` | Preflight → execute → analyze → settle |
| Evidence | `evidence/` | `RunRecord`, `EvidenceStore`, hashing |
| Replay / compare | `replay/` | Trajectories, divergence, ancestry, seed matrices, diagnosis |
| Analysis / ablation | `analysis/` | Statistics, causal helpers, ablation scaffolding |
| Learning (legacy) | `learning/` | `BehaviorExtractor`, `KnowledgeState`, strategy traces — pre-architecture helpers |
| Experiments | `experiments/exp042/` | Compatibility adapter demo; science injected from lab |
| Environments | `environments/craftax.py`, `minigrid.py` | Placeholder adapters — review candidates for lab relocation |
| Reporting | `reporting/strategy_graph.py` | Trivial dict builder, not a cognitive graph |

**Test surface:** 52 framework unit tests (unittest), including 8 cognitive-state and 7 public-percept contract tests plus independent verifiers under `scripts/`.

### 1.2 `CognitiveState` (v1)

`CognitiveState` is a frozen, reference-based coordination snapshot:

- Schema: `cognitive_state.v1`
- Fields: `state_id`, `logical_step`, typed reference collections (`goals`, `needs`, `beliefs`, `predictions`, `memories`, `possible_actions`), `uncertainty_ppm`, `hard_constraint_ids`
- Deterministic canonical JSON + SHA-256 digest (frozen fixture digest verified independently)
- Collections normalized to sorted order by `ref_id`; cross-collection ID uniqueness enforced
- No scalar reward, no NL control fields, no selected action authority
- **Does not** contain live graph structure, activation levels, or working-memory capacity logic

`CognitiveReference` carries `ref_id`, `kind`, `source_system`, `logical_step`, optional `confidence_ppm`, `evidence_ids`, and `memory_kind` (required for memory refs). Three memory roles are already distinguished: `episodic`, `semantic`, `procedural`.

### 1.3 `PublicPercept` (v1)

Environment-neutral percept envelope: `percept_id`, `modality`, `source_system`, `logical_step`, `content_sha256`, `confidence_ppm`, `evidence_ids`. Raw payloads stay outside the framework. Shared validation lives in `cognition/_validation.py`.

### 1.4 What partially supports the target architecture

| Target concept | Existing support | Gap |
| --- | --- | --- |
| Immutable auditable snapshots | `CognitiveState`, `PublicPercept` digests | No snapshot of live active graph / WM |
| Reference-based coordination | `CognitiveReference` | No refs to active-graph nodes or WM slots |
| Memory role separation | `MemoryKind` enum on refs | No episodic/semantic/procedural stores or records |
| Provenance / fail-closed IDs | `_validation.py` forbidden tokens | Not yet wired to active cognition |
| Logical time | `logical_step` on state/refs/percepts | No tick engine tying perception → activation → WM |
| Deterministic serialization | `canonical_json()`, `digest()` pattern | Reusable pattern, not yet on graph/WM |
| Replay infrastructure | `replay/` trajectories, divergence, compare | Replays experiment events, not cognitive runtime steps |
| Evidence / audit | `EvidenceStore`, hashing, run records | No cognitive-event ledger yet |
| Event streams | None in cognition | `reporting/timeline.py` is reporting-only |
| Graphs | `replay/ancestry.py` (run ancestry) | Not a cognitive relational graph |
| Ranking | `replay/seed_diagnosis.py` cohort contrast | Not memory retrieval ranking |
| Working memory | Documented only | Not implemented |
| Activation | Documented only | Not implemented |
| Retrieval / gaps | Documented only | Not implemented |

### 1.5 What must remain unchanged

- `CognitiveState` v1 schema and frozen digest (`32c435fe…07f7`) until a deliberate v2 migration with compatibility tests
- `CognitiveReference` v1 and `PublicPercept` v1 contracts
- Framework-never-imports-lab rule
- Evidence/replay/compare public APIs used by lab adapters
- Deterministic serialization conventions (sorted keys, ppm integers, explicit `None` for unknown)
- EXP-042 adapter as compatibility demo (not a pattern for new science)
- Historical frozen evidence must not be reinterpreted

### 1.6 Legacy / duplication risks

| Item | Risk | Recommendation |
| --- | --- | --- |
| `learning/knowledge_state.py` | Mutable list-based “concepts/strategies” — pre-architecture | Do not extend; future semantic memory is a new contract |
| `learning/behavior.py`, `strategy_trace.py` | Simple dataclasses for old learning reports | Keep; not cognitive runtime |
| `reporting/strategy_graph.py` | Name collision with “graph” | Rename only if it causes import confusion; not a cognitive graph |
| `environments/craftax.py`, `minigrid.py` | Experiment-named env stubs in framework | Audit for lab relocation; not active cognition |
| Brain-inspired doc package tree | Large prospective layout | Do not scaffold empty packages per DRY gate |

---

## 2. Gap analysis (relative to active-cognition architecture)

### 2.1 Missing abstractions (framework)

| Component | Priority for foundation | Notes |
| --- | --- | --- |
| `ActiveCognitiveGraph` | **P0** | Small runtime relational workspace |
| `WorkingMemory` | **P0** | Bounded admission/eviction with reasons |
| `PrimedMemory` | **P1** | Explicit LTM → primed → WM ladder |
| `ActivationPolicy` / `ActivationRecord` | **P0** | Configurable, inspectable, deterministic |
| `ActivationEngine` / runtime | **P0** | Decay, spread, promote, evict |
| `CognitiveGap` / `InformationNeed` | P2 | Drives retrieval; after WM foundation |
| `RetrievalController` + ports | P2 | After gaps and memory role records |
| Episodic / semantic / procedural **records** + ports | P2 | Distinct contracts; backends pluggable |
| Unified `Event` structure | P1 | Reusable across memory, planning, language |
| `CognitiveEventBus` port | P1 | In-memory backend first |
| `ActiveCognitionSnapshot` | **P0** | Bridge live runtime → `CognitiveState` |
| World model / prediction delta | P3 | Interface dependency only when needed |
| Language port | P4 | Later stage |

### 2.2 Partial implementations to reuse

- **`_validation.py`**: identifier, ppm, opaque-id rules → reuse for node/edge IDs
- **`CognitiveState.digest()` pattern** → apply to graph/WM snapshots
- **`replay/trajectory.py`**: step sequences — future cognitive replay may mirror this API
- **`artifacts/hashing.py`**: file hashing for evidence, not cognitive state
- **`MemoryKind`**: already encodes LTM roles on references; WM refs can use episodic default or explicit kind

### 2.3 Architectural alignment

The existing docs (`BRAIN_INSPIRED_COGNITIVE_ARCHITECTUR.md`) already describe:

- `CognitiveState` as compact index, not whole brain
- Separate fast events, persistent state, modulatory channels
- WM bounded; no NL control protocol
- Memory backends pluggable

The **new center of gravity** is explicit: recurrent **Active Cognitive Graph + WM + Activation + Retrieval**, with `CognitiveState` as immutable snapshot of that live runtime. Current code implements only the snapshot half (references without live graph).

---

## 3. Framework vs Learning Lab ownership

| Concern | Framework | Learning Lab |
| --- | --- | --- |
| `ActiveCognitiveGraph`, node/edge type enums | Generic contracts + reference runtime | Experiment-specific node semantics (what “cat” means in Craftax) |
| `WorkingMemory` / `PrimedMemory` capacity & policy | Contracts, admission/eviction machinery | Thresholds, weights, ablation configurations |
| `ActivationPolicy` weights | Schema + validation | Injected experiment values |
| `RetrievalController` | Port, ranking signal schema | What to retrieve for a task; relevance tuning |
| `CognitiveGap` types | Generic gap kinds | Which gaps matter in an environment |
| Perception decoding | `PublicPercept` envelope | Environment adapters, feature extraction |
| Episodic events content | `Event` predicate schema | Simulator event instantiation |
| Redis / vector / graph DB | Optional backends behind ports | Deployment choice |
| Evidence interpretation | Store, hash, replay compare | Scientific claims |
| Seeds, thresholds, pass/fail | Never | Always |

**Promotion rule unchanged:** lab prototype → duplication audit → generic framework contract → framework tests → pin commit in lab.

---

## 4. Revised architecture diagram

```text
                    Goals / Needs / Value (refs in CognitiveState)
                            |
                      top-down bias (future)
                            |
                            v
PublicPercept -----> Active Cognitive Graph <------ Predictions (refs)
         |                  |
         |            Working Memory  ←── bounded, admission/eviction
         |                  |
         |         Primed Memory (candidates)
         |                  |
         |         Activation Engine (decay, spread, thresholds)
         |                  |
         |         Cognitive Gaps (future) → Retrieval Controller (future)
         |                  |
         |    +-------------+-------------+
         |    v             v             v
         | Episodic    Semantic    Procedural  (LTM ports, future)
         |    +-------------+-------------+
         |                  |
         v                  v
              Active Cognitive Graph (updated)
                            |
              Reasoning / Planning / Executive (future)
                            |
                            v
                         Action proposals (refs in CognitiveState)

Live runtime layers:
  InMemoryActiveCognitionRuntime  (v1)
      ├── ActivationPolicy (injected)
      ├── ActiveCognitiveGraph
      ├── WorkingMemory
      ├── PrimedMemory
      └── activation trace records

Snapshot boundary:
  ActiveCognitionSnapshot  --project-->  CognitiveState v1 (immutable, auditable)
      │
      +--> evidence / replay / compare / ablation (existing machinery)

Storage (later, behind ports):
  ActivationStore, CognitiveEventBus, MemoryStore
      ├── in-memory (required for tests)
      └── Redis / PG / graph / vector (optional backends)
```

---

## 5. Revised incremental roadmap

Dependency-aware ordering (adjustments from user proposal noted):

| Phase | Content | Rationale |
| --- | --- | --- |
| **F1 (current)** | `CognitiveState`, `PublicPercept` | Complete; CA-I1 lab consumer gate pending |
| **F1.5 (new)** | Active cognition foundation | **Must precede** value/homeostasis in *runtime* terms because perception feeds activation; can proceed **in parallel** with F2 contracts |
| **F2** | Value, safety, homeostasis contracts | Independent typed records; can reference active graph nodes by ID |
| **F3** | Belief / uncertainty records | Beliefs as graph nodes + refs |
| **F4** | Retrieval foundation | Requires WM + gaps + memory role records |
| **F5** | World model + prediction errors | Needs stable event + graph delta contract |
| **F6** | Executive / attention / arbitration | Consumes WM + proposals |
| **F7** | Planning / skills / credit | Needs procedural memory port |
| **F8** | Language / social | Last; LLM as port only |

**Change from prior roadmap:** Insert **F1.5 Active Cognition** after perception compatibility, **before** full memory stores. Prior roadmap placed working memory at F4; active cognition WM is a *runtime workspace*, distinct from LTM episodic/semantic/procedural stores. LTM ports remain F4; runtime WM is F1.5.

**Change from brain-inspired doc §31:** Value/homeostasis (old priority 2) can proceed as **contracts** in parallel, but the **recurrent runtime loop** starts with active graph + activation.

---

## 6. Proposed package / API layout

Additive only; no empty packages:

```text
src/cogniverse_framework/cognition/
    __init__.py              # extend exports
    _validation.py           # unchanged
    state.py                 # CognitiveState v1 frozen
    perception.py            # PublicPercept v1 frozen
    active/
        __init__.py
        graph.py             # ActiveCognitiveGraph, nodes, edges, enums
        memory.py            # WorkingMemory, PrimedMemory, items
        activation.py        # ActivationPolicy, ActivationRecord, engine
        runtime.py           # InMemoryActiveCognitionRuntime
        snapshot.py          # ActiveCognitionSnapshot → CognitiveState projection
```

**Public exports (v1 milestone):**

```python
# cognition.active
ActiveCognitiveGraph, ActiveCognitiveNode, ActiveCognitiveEdge
NodeCategory, EdgeRelation
WorkingMemory, PrimedMemory, WorkingMemoryItem, PrimedMemoryItem
ActivationPolicy, ActivationRecord, ActivationSource
InMemoryActiveCognitionRuntime
ActiveCognitionSnapshot
```

**Not in v1:** `CognitiveEventBus`, `RetrievalController`, Redis backends, `CognitiveState` v2 fields.

---

## 7. Smallest safe implementation milestone (F1.5)

**Goal:** Prove deterministic active cognition substrate without LTM, retrieval, Redis, or `CognitiveState` schema break.

**In scope:**

1. `ActiveCognitiveGraph` v1 — typed nodes, typed edges, activation ppm, provenance, deterministic digest
2. `WorkingMemory` v1 — capacity, admission, eviction with reasons
3. `PrimedMemory` v1 — candidates below WM capacity threshold
4. `ActivationPolicy` + `ActivationRecord` — all weights/thresholds injected
5. `InMemoryActiveCognitionRuntime` — perceive, spread, tick/decay, promote/evict
6. `ActiveCognitionSnapshot` — immutable bundle; `to_cognitive_state()` adds memory refs
7. Framework tests + verifier script
8. Documentation update (implemented vs proposed)

**Out of scope:**

- Redis, event bus backend, retrieval, cognitive gaps, world model, LLM
- `CognitiveState` v2 schema change
- Lab consumer integration (follows CA-I1 pattern)

**Demonstration scenario (test-backed):**

1. Add perceived node → receives activation boost  
2. Add associative edge → related node receives spread boost  
3. Advance logical time → decay reduces activation  
4. High activation → promoted to working memory  
5. Capacity pressure → lowest activation evicted with reason trace  
6. Snapshot digest stable across reconstruction  
7. Projected `CognitiveState` validates against v1 rules  
8. Operation sequence replay → identical snapshot digest  

---

## 8. Risks and compatibility concerns

| Risk | Mitigation |
| --- | --- |
| Breaking `CognitiveState` v1 digest | Do not modify `state.py`; snapshot projects into v1 |
| Conflating WM with `CognitiveState` | WM is live runtime; state is snapshot refs only |
| Duplicating `KnowledgeState` | New contracts; do not extend legacy learning module |
| Redis as cognitive theory | Ports only in later milestone; tests use in-memory |
| Speculative abstractions | No event bus/retrieval until consumer exists |
| Name collision “graph” | `ActiveCognitiveGraph` prefix; strategy_graph unchanged |
| Integer activation overflow | Clamp to `[0, 1_000_000]` ppm after each update |
| Non-deterministic ordering | Sort nodes/edges/items by ID everywhere |
| Scientific overclaim | Tests prove contract determinism, not biological fidelity |

---

## 9. Test plan

### 9.1 Unit tests (`tests/test_active_cognition.py`)

| Test | Asserts |
| --- | --- |
| Graph immutability + schema version | Frozen dataclass, validation errors |
| Deterministic serialization | Same digest regardless of input order |
| Perception boost | New node reaches expected activation |
| Spreading activation | Neighbor gains boost via typed edge |
| Decay over logical step | Monotonic decrease without inputs |
| WM promotion | Above threshold enters WM |
| Capacity eviction | Lowest activation removed; reason recorded |
| Primed ladder | Between thresholds → primed, not WM |
| Snapshot replay | Operation log → identical digest |
| CognitiveState projection | Valid v1 state; existing state tests still pass |
| Policy injection | Different policies → different activations |
| Forbidden identifiers | Fail-closed on private/evaluator markers |

### 9.2 Regression

- Full `unittest discover` (52+ tests) must remain green
- `scripts/verify_cognitive_state_contract.py` digest unchanged
- `scripts/verify_public_percept_contract.py` unchanged

### 9.3 Future tests (not this milestone)

- Lab CA-I1 equivalence with active runtime enabled
- Retrieval driven by `CognitiveGap`
- Event bus replay with Redis backend
- Ablation: disable spreading activation

---

## 10. Implementation status

| Item | Status |
| --- | --- |
| This audit | **Complete** |
| F1.5 active cognition code | **Implemented** — see [ACTIVE_COGNITION_V1.md](ACTIVE_COGNITION_V1.md) |
| Coordinator + pluggable backends | **Implemented** — see [COGNITION_BACKENDS_V1.md](COGNITION_BACKENDS_V1.md) |
| Framework tests | **96/96 PASS** |
| Framework reference coordinator fixture | **Complete** — `tests/test_coordinator_fixture.py` |
| Lab consumer for active runtime | **Complete** (CA-I1/CA-P1) |
| F2 value/homeostasis machinery | **Complete** — see [VALUE_HOMEOSTASIS_V1.md](VALUE_HOMEOSTASIS_V1.md) |
| Scientific validation | **Not claimed** |

Passing tests demonstrate deterministic, auditable contracts — not that the activation policy is cognitively correct.
