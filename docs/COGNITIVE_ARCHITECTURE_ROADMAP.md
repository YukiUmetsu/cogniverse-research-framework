# Cognitive architecture framework roadmap

**Plan date:** 2026-08-26  
**Scope:** reusable platform contracts and machinery, not experiment science

## Direction

The research framework will evolve from a repeatable experiment toolbox into the reusable substrate for Cogniverse's brain-inspired cognitive architecture.

It continues to own execution, evidence, replay, comparison and audit. It will additionally own generic typed contracts and ports that let cognitive subsystems work together without natural language or experiment-specific coupling.

The learning lab remains the owner of scientific hypotheses, environments, frozen protocols, outcomes and claims.

## Current strengths

The audited framework already has useful platform foundations:

- execution lifecycle and evidence storage;
- replay-only validation;
- typed sequence divergence, ancestry and seed comparison;
- domain-agnostic failure diagnosis and audit cards;
- thin data-injected adapter patterns;
- a documented boundary that keeps seeds, timing and claim wording in the lab.

These are precursors. The framework now provides the first shared cognitive-state and public-percept contracts, but not homeostasis/value contracts, prediction-error lifecycle, typed memory stores or executive/arbitration ports.

The built-in `Exp042Adapter` remains a compatibility/demo surface. New framework APIs should not use experiment-numbered names.

## Target package direction

Proposed additive structure:

```text
src/cogniverse_framework/
    cognition/
        state.py
        perception.py
        beliefs.py
        goals.py
        value.py
        homeostasis.py
        world_model.py
        memory.py
        planning.py
        executive.py
        arbitration.py
        learning.py
        language.py
        legacy.py
    evidence/
    replay/
    execution/
    analysis/
    environments/
```

This layout is directional. Add only the smallest package required by the current frozen interface gate.

## Architecture constraints

- Framework code never imports the learning lab.
- Cognitive contracts contain no experiment IDs, seeds, pass thresholds or task semantics.
- Cross-module decision data is typed and versioned.
- Natural-language fields cannot control goals, values, executive choices or actions.
- LLM requests/responses are optional interface records marked hypothetical or presentation-only.
- Hard constraints are separate from soft value.
- Scalar reward appears only through an explicit legacy adapter.
- Predictions remain hypothetical until bound to an executed empirical event.
- Episodic, semantic and procedural records remain distinct even if one backend stores them.
- All compatibility and schema migrations are deterministic and auditable.

## Phase F0 — documentation and ownership

Deliverables:

- DRY and cross-repository ownership policy;
- this framework roadmap;
- README and architecture links;
- prospective placement check for new PRs.

No code behavior changes.

## Phase F1 — minimal cognitive contracts

Status: **cognitive-state conformance complete; perception consumer conformance next**. `CognitiveState` and provenance-bearing `CognitiveReference` v1 passed exact legacy equivalence across two learning-lab loops in CA-I1. `PublicPercept` v1 now provides the smallest immutable public-perception envelope; its first unchanged Learning Lab consumer is still pending.

Research/engineering question:

> Can two different learning-lab loops exchange the same typed cognitive snapshot with exact legacy behavior?

First public contracts:

- `CognitiveState`
- `PublicPercept`
- `BeliefRef`
- `GoalRef`
- `NeedState`
- `PredictionRef`
- `MemoryRef`
- `ActionProposal`
- `HardConstraint`
- `SelectedAction`
- `LearningUpdateRef`

Framework responsibilities:

- immutable data models;
- validation;
- deterministic serialization;
- schema versions;
- fail-closed unknown/private/evaluator handling;
- protocols/ports rather than task implementations;
- legacy adapter interfaces.

Learning-lab responsibilities:

- select two structurally different loops;
- supply environment-specific adapters and fixtures;
- preregister exact replay equivalence;
- interpret scientific meaning.

Exit gate:

- framework unit/contract tests;
- two lab consumer fixtures;
- exact legacy action/event/evidence equivalence;
- no LLM dependency;
- no held-out task outcome needed.

## Phase F2 — value, safety and homeostasis contracts

Add only generic records and policies:

- versioned `ValueVector`;
- `ValueEstimate` with uncertainty and horizon;
- `HardConstraint` and violation record;
- `NeedState` with level, target, deficit and provenance;
- `HomeostaticUpdate`;
- `LegacyScalarRewardAdapter`.

Keep environment need dynamics and scientific weighting configurations injectable from the lab.

Exit gate:

- deterministic traces;
- configuration/version provenance;
- scalar reward cannot silently populate survival/safety;
- controlled lab mechanism plus ablation;
- second domain uses unchanged contracts.

## Phase F3 — world-model and prediction-error lifecycle

Add:

- `Prediction` and outcome distributions;
- `PredictionSet`;
- `PredictionMatch`;
- per-feature `PredictionError`;
- separate `ValueError`;
- `ModelUpdateRecord`;
- generic calibration and error metrics;
- replay/audit reconstruction.

Do not implement one benchmark's transition model in the framework. Model algorithms may be promoted only after the ownership gate.

## Phase F4 — memory roles and consolidation

Add generic records/ports for:

- working memory;
- episodic events;
- semantic knowledge;
- procedural skills;
- consolidation;
- forgetting/tombstones;
- memory retrieval requests and results;
- provenance-preserving compression.

Storage backends remain plugins. A vector database is one backend, not the memory model.

## Phase F5 — executive, planning and arbitration ports

Add:

- attention and goal proposals;
- subsystem query requests;
- plan graphs;
- confidence/conflict triggers;
- action proposals;
- arbitration decisions and rejected reasons;
- stop/replan/explore control transitions;
- trace reconstruction.

Start with interfaces and transparent reference policies. Do not install an LLM as the default controller.

## Phase F6 — skill and credit machinery

Add generic:

- skill graphs and preconditions;
- formation/consolidation evidence;
- reliability and transfer records;
- delayed credit assignments;
- links to prior state, prediction, plan and action;
- counterfactual records that remain non-empirical.

## Phase F7 — language and social interfaces

Language:

- read-only explanation/query ports;
- typed hypothesis proposals;
- presentation provenance;
- injection/leakage tests;
- control loop remains complete without language.

Social cognition:

- later generic other-agent belief/goal/trust records;
- no game-specific strategy in framework;
- private information boundaries explicit.

## Cross-repository delivery workflow

For each phase:

1. audit lab duplicates and current framework APIs;
2. write an ownership decision;
3. freeze the generic contract in the framework;
4. test without lab imports;
5. merge and record exact framework commit;
6. pin that commit/release in the lab;
7. add thin lab consumers;
8. run exact compatibility and module ablation;
9. promote no experiment-specific science back into the framework.

## Initial cleanup candidates

These are audits, not automatic deletion tasks:

- document `Exp042Adapter` as compatibility/demo-only;
- audit whether experiment scaffolding under framework `experiments/` encourages science to leak into the framework;
- inspect the placeholder Craftax/MiniGrid adapters and decide whether they are contract fixtures or misplaced domain implementations;
- consolidate duplicate compare/statistics/ablation helpers behind coherent typed APIs;
- remove or deprecate no-op/stub surfaces only after consumer search and compatibility review.

Existing code is preserved until each cleanup has a test-backed migration path.

## Success measures

The framework migration succeeds when:

- new experiments rarely define their own generic data models;
- duplicated mechanism code declines;
- the same cognitive contracts work across environments;
- framework changes have multiple consumers or foundational contract justification;
- lab experiment folders become thinner;
- exact provenance and replay remain strong;
- module ablations are easier, not harder;
- no LLM or natural-language string silently becomes the controller.
