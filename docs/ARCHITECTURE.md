# Architecture

## Active cognition substrate

The live runtime centers on a small **Active Cognitive Graph** with **Working Memory**, **Primed Memory**, and a deterministic **Activation** mechanism. `CognitiveState` remains the immutable snapshot boundary for evidence, replay, and audit — it is not mutable working memory.

| Concept | Role | Status |
| --- | --- | --- |
| `CognitiveState` | Immutable auditable snapshot | Implemented (v1) |
| `ActiveCognitiveGraph` | Live relational workspace | Implemented (v1) |
| `WorkingMemory` | Bounded active material | Implemented (v1) |
| `PrimedMemory` | Partially activated candidates | Implemented (v1) |
| `ActivationPolicy` | Injected decay/boost thresholds | Implemented (v1) |
| `RetrievalController` | Goal/gap-driven memory search | Proposed |
| Long-term memory ports | Episodic / semantic / procedural | Proposed |

Redis and other stores are optional backends only; framework tests run without them.

## Prospective cognitive-architecture boundary

The framework is the reusable substrate, not the artificial organism's scientific configuration.

```text
learning lab
    ├─ environment and public perception adapters
    ├─ experiment hypotheses, values/configurations and protocols
    ├─ thin subsystem implementations under test
    └─ imports
          ↓
framework
    ├─ typed CognitiveState and cognitive subsystem ports
    ├─ generic evidence/provenance/versioning
    ├─ replay, comparison, metrics and ablation
    └─ no lab import and no experiment science
```

Reusable cross-module concepts belong here: beliefs, uncertainty, needs, multi-dimensional value, hard constraints, predictions/errors, memory-role records, plans, action proposals, executive/arbitration traces and learning-update provenance.

Environment mechanics, native semantics, seeds, thresholds, policy configurations and scientific interpretation stay in the learning lab. An LLM is an optional interface client; no natural-language field may silently control the cognitive loop.

Before adding code, apply [the DRY and ownership policy](DRY_AND_CODE_OWNERSHIP.md). The phased platform plan is [the cognitive architecture roadmap](COGNITIVE_ARCHITECTURE_ROADMAP.md).

## Boundaries

| Layer | Owns | Does not own |
| --- | --- | --- |
| **Framework** (`cogniverse_framework`) | Generic cognitive contracts/ports, replay/compare APIs, artifacts, evidence stores, execution lifecycle | Experiment seeds, mutation timings, claim strings, lab-specific strategy IDs, environment mechanics |
| **Learning lab** | Experiment science, environments, injected fixtures/configuration, claim naming, pinned framework dependency | Reimplementing generic cognitive contracts, provenance, divergence, ancestry, metrics or ablation helpers |

Experiment lifecycle:

```
preflight → execute → analyze → compare → settle → archive
```

## Replay / compare surface

Prefer the coherent API under `cogniverse_framework.replay`:

- `compare_seed_matrix` / `compare_runs` — typed seed and run diffs
- `audit_sequence_divergence`, `find_later`, `first_divergence` — sequence audits
- `shared_ancestry`, `first_reach_parents`, `ancestry_path` — ancestry graphs
- `diagnose_seed_failures` / `SeedProfile` — contrast repeatedly failing seeds
  against a reference cohort on caller-supplied metrics and milestones

Result types (`DivergenceResult`, `LaterLookup`, `SeedMatrixResult`,
`SeedFailureDiagnosis`, …) live in `cogniverse_framework.replay.types` and
`replay.seed_diagnosis_types`. Compatibility shims remain in
`replay.comparison`, `replay.seed_matrix`, and `research.MutationAnalysis`.

Seed-failure diagnosis is intentionally domain-agnostic: the lab extracts
metrics from archived evidence and may attach classifier labels; the framework
owns the cohort contrast bookkeeping.

## EXP-042 adapter

`Exp042Adapter` demonstrates the adapter contract. Pass `seed`,
`baseline_scores`, `candidate_scores`, and `learning_evidence` from the lab;
the framework does not hardcode those values.
