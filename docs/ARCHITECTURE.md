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

Result types (`DivergenceResult`, `LaterLookup`, `SeedMatrixResult`, …) live in
`cogniverse_framework.replay.types`. Compatibility shims remain in
`replay.comparison`, `replay.seed_matrix`, and `research.MutationAnalysis`.

## EXP-042 adapter

`Exp042Adapter` demonstrates the adapter contract. Pass `seed`,
`baseline_scores`, `candidate_scores`, and `learning_evidence` from the lab;
the framework does not hardcode those values.
