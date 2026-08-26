# DRY and code-ownership policy

**Adopted:** 2026-08-26  
**Applies to:** new framework and learning-lab work  
**Does not rewrite:** existing experiment history or compatibility APIs

## Principle

Cogniverse should solve a reusable problem once.

Experiment code is allowed to be specific. Infrastructure and cognitive machinery should not be copied into experiment folders merely because copying is faster for one run.

DRY means "do not repeat knowledge," not "force every similar-looking line through one function." An abstraction is justified when it owns a stable concept, invariant or algorithm that more than one experiment can use.

## Dependency direction

```text
cogniverse-learning-lab
    ├─ research questions, protocols and experiment adapters
    ├─ environment-specific implementations
    └─ imports
          ↓
cogniverse-research-framework
    ├─ generic cognitive contracts and subsystem ports
    ├─ reusable provenance, memory, prediction and value records
    ├─ execution, evidence, replay, comparison and ablation
    └─ never imports the learning lab
```

The framework must not know a lab experiment number, seed block, pass threshold, scientific claim or evaluator answer unless retained as an explicitly deprecated compatibility example.

## Placement decision

| Code or data | Experiment folder | Shared learning-lab package | Research framework |
| --- | --- | --- | --- |
| Hypothesis and claim wording | Yes | No | No |
| Frozen seed list, threshold and protocol | Yes | No | No |
| One-time evaluator gate | Yes | Maybe, if reused | No |
| Thin adapter wiring frozen experiment inputs to shared APIs | Yes | No | No |
| Environment-specific public observation decoder | Only as first prototype | Yes after reuse is likely | Protocol only |
| Craftax/MiniGrid mechanics or semantic adapter | No unless truly one-off | Yes | No |
| Generic `CognitiveState`, beliefs, needs, values, predictions or memory contracts | No | No | Yes |
| Generic serialization, schema migration and validation | No | No | Yes |
| Generic provenance, replay, evidence and audit ledgers | No | No | Yes |
| Generic module ablation or comparison machinery | No | No | Yes |
| Environment-neutral planner/executive/arbitration ports | No | No | Yes |
| A cognitive algorithm proven reusable across domains | No | Prototype may start here | Yes after promotion |
| Report-specific interpretation | Yes | No | No |
| Generic metric calculation | No | Only if environment-specific | Yes |

## Reuse test before writing code

Before adding a nontrivial helper to an experiment, answer:

1. Can the concept be named without the experiment number?
2. Are its inputs and outputs meaningful in another environment?
3. Does it enforce an invariant the platform should share?
4. Is similar logic already present elsewhere?
5. Will the next likely experiment need it?
6. Can task-specific constants and semantics be injected?
7. Can it be tested without opening held-out outcomes?
8. Does it belong to a cognitive interface or research lifecycle?

If questions 1–3 are yes and either 4 or 5 is yes, default to a shared implementation.

## Extraction rule

A truly uncertain first prototype may live in an experiment folder when extracting it would guess at the wrong abstraction.

Before a second implementation or copy:

1. compare the two use cases;
2. identify the stable common contract;
3. move the common mechanism to the appropriate shared package;
4. leave thin compatibility adapters in old experiments;
5. add consumer contract tests;
6. preserve exact frozen behavior and evidence;
7. delete no historical evidence.

No third copy is allowed without a written exception explaining why the semantics are genuinely different.

## Framework admission gate

Code belongs in this repository only if all relevant statements are true:

- it is environment- and experiment-neutral;
- lab-specific values are injected;
- the framework does not import the lab;
- public API ownership and schema version are clear;
- unknown/invalid/private/evaluator inputs fail closed;
- deterministic serialization/replay is tested where promised;
- at least two consumers exist or a foundational cross-module contract makes reuse intrinsic;
- a simpler API cannot meet the same need;
- migration and compatibility behavior are documented.

Foundational contracts such as `CognitiveState` may enter before two full consumers, but must have at least two contract fixtures and a planned second consumer.

## Learning-lab shared package gate

Some reusable code is not framework code.

Keep it in the learning lab when it is reusable across experiments but tied to:

- one simulator's public observation schema;
- environment-specific replay or dynamics;
- domain-specific feature extraction;
- native runtime provenance;
- one benchmark family.

Experiments import these shared lab packages. They do not copy them.

## Experiment-folder allowance

Experiment folders should normally contain only:

- a preregistered hypothesis;
- protocol and evidence manifests;
- frozen constants and seeds;
- thin dependency injection;
- truly study-specific stimulus/case generation;
- evaluator gates and claim wording;
- result/report artifacts.

A large algorithm, serializer, ledger, simulator helper or repeated data model inside an experiment folder is a review warning.

## Cognitive-architecture rule

The framework is the default owner of reusable typed communication among cognitive systems:

- percepts and candidate representations;
- beliefs, confidence and uncertainty;
- goals and working-state references;
- needs, hard constraints and multi-dimensional value;
- predictions, prediction matches and prediction errors;
- episodic, semantic and procedural memory records;
- action proposals, arbitration and executive traces;
- model/memory learning updates;
- LLM-interface requests and responses marked as non-controlling.

Natural-language control fields are forbidden in these contracts. An LLM is an optional client/interface, not the framework's executive controller.

## Promotion workflow

When a lab mechanism becomes reusable:

```text
lab prototype
→ duplication/ownership audit
→ generic contract in framework branch
→ framework focused tests
→ framework PR and merge
→ pin framework commit/release in lab
→ replace lab copies with thin adapters
→ exact regression and frozen-evidence check
```

Do not make simultaneous unpinned edits in both repositories and call them one verified result. Record the exact framework commit used by the lab.

## Review checklist

Every implementation PR should state:

- why the code is experiment-specific, lab-shared or framework-generic;
- search results for existing similar code;
- extracted constants/semantics;
- current and planned consumers;
- compatibility impact;
- tests and ablations;
- whether an LLM or natural language enters the control path;
- whether any scientific outcome was opened.

The reviewer should reject avoidable duplication even when the new copy passes its local tests.

## Exceptions

An exception is acceptable for:

- frozen historical code whose modification would damage reproducibility;
- a genuinely one-time evaluator;
- a prototype whose stable abstraction is not yet knowable;
- a compatibility shim required by old imports.

Label the exception and add a removal or reevaluation condition. "It was faster" is not an exception.
