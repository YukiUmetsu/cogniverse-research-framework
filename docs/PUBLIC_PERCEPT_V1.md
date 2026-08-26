# PublicPercept v1

## 1. Background knowledge I need to know

Perception turns raw environmental signals into records other cognitive systems can use. A percept is not automatically a belief: it says what public input was received and where its stored content can be verified, without claiming the interpretation is true.

`PublicPercept` is a small immutable envelope. Raw images, grids, audio, or simulator objects stay in environment/perception-owned stores. The envelope carries only stable identity, broad modality, logical time, content SHA-256, provenance references, and confidence or explicit unknown.

## 2. What we are trying to test

Can the framework represent public percepts deterministically and fail closed on missing provenance, invalid confidence, noncanonical content identity, or forbidden information markers?

Architecture placement: this is the typed output boundary of perception. It changes no prediction error, value error, memory update, or control decision. Existing `CognitiveState` and legacy learners remain unchanged.

Lane separation: native Learning Lab research studies task-world learning and information-value scheduling. This contract tests simulator-neutral perception provenance, not reward, survival, resources, policy, or native transfer.

## 3. Expectations vs result

The test-first run failed with the expected import error because no percept contract existed. The minimal implementation then passed all focused tests and an independent verifier twice.

Validation shared with `CognitiveState` moved to one internal module, avoiding a second copy while preserving the existing state fixture byte for byte.

## 4. Data

| Metric | Result | Meaning |
| --- | ---: | --- |
| Focused perception tests | **6/6 PASS** | Contract, rejection, immutability, and serialization behavior |
| Independent checks | **7/7 PASS twice** | Separate fixture reconstruction agreed |
| Existing state digest | `32c435fe…07f7` | `CognitiveState` serialization stayed unchanged |
| Percept digest | `6deedb68…ddcf` | Deterministic `PublicPercept` fixture identity |
| Raw payload fields | **0** | Large observations remain subsystem-owned |
| Decision/language fields | **0** | No reward, selected action, prompt, or reasoning authority |
| LLM dependencies | **0** | The contract works without language models |
| Scientific outcomes opened | **0** | Framework-interface evidence only |

## 5. What is next

Pin the exact merged framework commit in Learning Lab, add a thin shared lab adapter for one existing public observation source, and preregister exact legacy equivalence. Do not add environment decoding to the framework.

After one consumer passes, decide whether a separate perception-frame/port is actually required from observed usage. Avoid designing speculative ports before a concrete consumer demonstrates the need.

## 6. How docs and main branch were updated

Framework version `0.4.0` adds:

- `PublicPercept` and `PerceptModality`;
- shared cognitive validation helpers;
- focused tests and an independent verifier;
- README and cognitive-architecture roadmap updates.

Learning Lab is unchanged until the framework PR is merged and its exact identity can be pinned.

## 7. Other important info / limitations

- This is an interface contract, not perception learning or object recognition.
- The environment adapter supplies modality, confidence, evidence IDs, and the raw-content digest.
- SHA-256 identifies bytes; it does not prove those bytes are truthful or semantically correct.
- Identifier filtering is a narrow fail-closed boundary, not a complete information-security system.
- The contract does not promote a percept into a belief or accepted empirical knowledge.
- No simulator, held-out task outcome, or GitHub Actions research simulation ran.

## 8. Continue the research

Use the frozen contract unchanged in one Learning Lab consumer. Measure exact legacy behavior and provenance equivalence before introducing value/homeostasis or world-model updates.
