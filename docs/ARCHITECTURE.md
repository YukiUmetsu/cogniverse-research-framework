# Architecture

## Boundaries

| Layer | Owns | Does not own |
| --- | --- | --- |
| **Framework** (`cogniverse_framework`) | Replay/compare APIs, adapters as thin contracts, artifacts, evidence stores, execution lifecycle | Experiment seeds, mutation timings, claim strings, lab-specific strategy ids |
| **Learning lab** | EXP-042 science, injected fixture data, claim naming, CI pins of this package | Reimplementing generic divergence/ancestry helpers |

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
