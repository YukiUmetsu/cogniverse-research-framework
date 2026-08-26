# CognitiveState v1 foundation

## 1. Background knowledge I need to know

A cognitive architecture contains several systems that must exchange information without using English as their control protocol. `CognitiveState` is a small coordination snapshot: it points to goals, needs, beliefs, predictions, memories, possible actions and hard constraints while each subsystem keeps ownership of its larger data.

Confidence uses integer parts per million (`0` to `1,000,000`) so serialization is exact across runs. `None` means explicitly unknown. Episodic, semantic and procedural memory references stay distinct.

## 2. What we are trying to test

Can the framework provide one environment-neutral, immutable and deterministic state contract without introducing task policy, an LLM controller, scalar reward, or a universal memory database?

Ownership is framework-generic. No experiment seed, threshold, simulator meaning or scientific outcome belongs in this package.

## 3. Expectations vs result

The test-first run failed because `cogniverse_framework.cognition.state` did not exist. The minimal implementation then passed the focused contract suite and a separate dependency-free verifier.

The result is an engineering foundation, not a CA-I1 scientific pass. Two structurally different learning-lab consumers and exact legacy equivalence remain required.

## 4. Data

| Metric | Result | Meaning |
| --- | ---: | --- |
| Focused tests | 8/8 PASS | Immutability, validation, role separation and serialization |
| Independent checks | 7/7 PASS twice | Separate reconstruction agreed deterministically |
| Schema versions | 2 | `cognitive_state.v1` and `cognitive_reference.v1` |
| Memory roles | 3 | Episodic, semantic and procedural remain explicit |
| Natural-language control fields | 0 | No English decision channel |
| Scalar reward fields | 0 | Reward was not relabeled as value or homeostasis |
| Lab imports | 0 | Dependency direction remains one-way |
| Scientific outcomes opened | 0 | Interface-only evidence |

Canonical verifier digest: `32c435fe5230ade4ef5590c016fc39968fca2d9ab11744d4bfa27fcbe7ad07f7`.

## 5. What is next

1. Merge this generic contract and pin the exact framework commit in the learning lab.
2. Preregister CA-I1 with two structurally different legacy-loop fixtures.
3. Add thin identity adapters in the lab.
4. Require exact action, event and evidence equivalence with the adapter enabled and disabled.
5. Only after CA-I1 closes, introduce separate value, safety and homeostasis contracts.

## 6. How docs and main branch were updated

The framework adds the `cognition` package, focused tests, an independent verifier, this report, and roadmap/API documentation. No learning-lab experiment or historical evidence is modified by this framework milestone.

## 7. Other important info / limitations

- References point to subsystem-owned content; they do not contain full beliefs, plans or memories.
- Identifier filtering is a fail-closed boundary for obvious private/evaluator/future-answer markers, not a complete information-flow security system.
- `possible_actions` are proposals, not selected actions.
- Hard constraints are references only; constraint evaluation and arbitration are later contracts.
- No value vector, homeostatic update, prediction error, consolidation, planner or executive controller exists yet.
- No LLM is imported or required.

## 8. Continue the research

Use the unchanged v1 contract in two lab loops and measure exact legacy equivalence. A passing interface test will show that cognitive subsystems can share typed state safely; it will not show that the organism learns better until later controlled ablations test individual mechanisms.
