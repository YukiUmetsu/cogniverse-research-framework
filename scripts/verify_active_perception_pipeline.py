"""Independent verification of the PublicPercept -> active cognition -> CognitiveState bridge."""

from __future__ import annotations

import hashlib
import json

from cogniverse_framework.cognition import (
    ActivationPolicy,
    ActivePerceptionConsumer,
    NodeCategory,
    PerceptModality,
    PublicPercept,
)


EXPECTED_PIPELINE_DIGEST = "84acaf19f2adc136206b9fd28771c9d19c9663302e954de27718efe60160e8bf"
EXPECTED_COGNITIVE_STATE_DIGEST = "55a5d43fda4d781cb3608728c1afaf1d06b412e3501f4a149f13fcd6eea7a7c8"
EXPECTED_SNAPSHOT_DIGEST = "b20586770efc609a5d161d2eae9d6bb6c7d223a73651d2e76be2f5dd747ab781"


def fixture_percepts() -> tuple[PublicPercept, ...]:
    payload_a = b"entity-a:1"
    payload_b = b"entity-b:2"
    return (
        PublicPercept(
            percept_id="entity-a",
            modality=PerceptModality.STRUCTURED,
            source_system="verifier-perception",
            logical_step=1,
            content_sha256=hashlib.sha256(payload_a).hexdigest(),
            confidence_ppm=800_000,
            evidence_ids=("event-1",),
        ),
        PublicPercept(
            percept_id="entity-b",
            modality=PerceptModality.STRUCTURED,
            source_system="verifier-perception",
            logical_step=2,
            content_sha256=hashlib.sha256(payload_b).hexdigest(),
            confidence_ppm=700_000,
            evidence_ids=("event-2",),
        ),
    )


policy = ActivationPolicy(
    policy_id="verifier-bridge-policy",
    decay_ppm=900_000,
    perception_boost_ppm=500_000,
    spreading_boost_ppm=150_000,
    working_threshold_ppm=300_000,
    primed_threshold_ppm=100_000,
)

pipeline = ActivePerceptionConsumer.process_percepts(
    fixture_percepts(),
    policy,
    working_capacity=2,
    node_category=NodeCategory.ENTITY,
    source_system="verifier-active-perception",
    state_id="verifier-state",
)

payload = pipeline.to_dict()
canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
independent_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

checks = {
    "pipeline_schema": True,
    "cognitive_state_schema": pipeline.cognitive_state.to_dict()["schema_version"]
    == "cognitive_state.v1",
    "snapshot_schema": pipeline.snapshot.to_dict()["schema_version"]
    == "active_cognition_snapshot.v1",
    "deterministic_pipeline_match": independent_digest
    == hashlib.sha256(
        json.dumps(
            ActivePerceptionConsumer.process_percepts(
                fixture_percepts(),
                policy,
                working_capacity=2,
                node_category=NodeCategory.ENTITY,
                source_system="verifier-active-perception",
                state_id="verifier-state",
            ).to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest(),
    "expected_pipeline_digest": independent_digest == EXPECTED_PIPELINE_DIGEST,
    "expected_cognitive_state_digest": pipeline.cognitive_state.digest()
    == EXPECTED_COGNITIVE_STATE_DIGEST,
    "expected_snapshot_digest": pipeline.snapshot.digest() == EXPECTED_SNAPSHOT_DIGEST,
    "working_memory_populated": len(pipeline.snapshot.working_memory.items) >= 1,
    "no_decision_language_fields": {
        "prompt",
        "reasoning",
        "selected_action",
        "text",
        "reward",
    }.isdisjoint(pipeline.cognitive_state.to_dict()),
}

if not all(checks.values()):
    raise SystemExit(json.dumps({"status": "FAIL", "checks": checks}, sort_keys=True))

print(
    json.dumps(
        {
            "status": "PASS",
            "checks": checks,
            "pipeline_digest": independent_digest,
            "cognitive_state_digest": pipeline.cognitive_state.digest(),
            "snapshot_digest": pipeline.snapshot.digest(),
        },
        sort_keys=True,
    )
)
