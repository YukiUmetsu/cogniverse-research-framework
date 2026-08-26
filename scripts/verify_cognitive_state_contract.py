"""Independent, dependency-free verification of the v1 cognitive-state contract."""

from __future__ import annotations

import hashlib
import json

from cogniverse_framework.cognition import (
    CognitiveReference,
    CognitiveState,
    MemoryKind,
    ReferenceKind,
)


EXPECTED_DIGEST = "32c435fe5230ade4ef5590c016fc39968fca2d9ab11744d4bfa27fcbe7ad07f7"


def item(
    ref_id: str,
    kind: ReferenceKind,
    memory_kind: MemoryKind | None = None,
) -> CognitiveReference:
    return CognitiveReference(
        ref_id=ref_id,
        kind=kind,
        source_system="fixture",
        logical_step=4,
        confidence_ppm=800_000,
        evidence_ids=("evidence-b", "evidence-a"),
        memory_kind=memory_kind,
    )


state = CognitiveState(
    state_id="state-1",
    logical_step=5,
    goals=(item("goal-1", ReferenceKind.GOAL),),
    needs=(item("need-1", ReferenceKind.NEED),),
    beliefs=(item("belief-1", ReferenceKind.BELIEF),),
    predictions=(item("prediction-1", ReferenceKind.PREDICTION),),
    memories=(
        item("memory-2", ReferenceKind.MEMORY, MemoryKind.SEMANTIC),
        item("memory-1", ReferenceKind.MEMORY, MemoryKind.EPISODIC),
    ),
    possible_actions=(item("action-1", ReferenceKind.ACTION),),
    uncertainty_ppm=250_000,
    hard_constraint_ids=("constraint-b", "constraint-a"),
)

payload = state.to_dict()
canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
independent_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

checks = {
    "schema_version": payload["schema_version"] == "cognitive_state.v1",
    "reference_schema_versions": all(
        record["schema_version"] == "cognitive_reference.v1"
        for group in (
            "goals",
            "needs",
            "beliefs",
            "predictions",
            "memories",
            "possible_actions",
        )
        for record in payload[group]
    ),
    "deterministic_order": [record["ref_id"] for record in payload["memories"]]
    == ["memory-1", "memory-2"],
    "no_decision_language_fields": {
        "prompt",
        "reasoning",
        "selected_action",
        "text",
    }.isdisjoint(payload),
    "no_scalar_reward_field": "reward" not in payload,
    "independent_digest_match": independent_digest == EXPECTED_DIGEST,
    "implementation_digest_match": state.digest() == EXPECTED_DIGEST,
}

if not all(checks.values()):
    raise SystemExit(json.dumps({"status": "FAIL", "checks": checks}, sort_keys=True))

print(
    json.dumps(
        {
            "status": "PASS",
            "checks": checks,
            "canonical_digest": independent_digest,
        },
        sort_keys=True,
    )
)
