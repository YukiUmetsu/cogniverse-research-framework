"""Independent, dependency-free verification of the active cognition snapshot contract."""

from __future__ import annotations

import hashlib
import json

from cogniverse_framework.cognition import (
    ActivationPolicy,
    EdgeRelation,
    InMemoryActiveCognitionRuntime,
    NodeCategory,
)


EXPECTED_DIGEST = "e8ac96a64dd8af8f7a88c6a6592c2409aadb2d0b746976ecf90e5a5b24eac216"


def build_snapshot():
    policy = ActivationPolicy(
        policy_id="verifier-policy",
        decay_ppm=900_000,
        perception_boost_ppm=500_000,
        spreading_boost_ppm=150_000,
        working_threshold_ppm=300_000,
        primed_threshold_ppm=100_000,
    )
    operations = (
        {
            "op": "add_perceived_node",
            "node": {
                "node_id": "node-a",
                "category": NodeCategory.ENTITY,
                "source_system": "perception",
                "logical_step": 1,
                "evidence_ids": ("evidence-1",),
            },
        },
        {
            "op": "add_perceived_node",
            "node": {
                "node_id": "node-b",
                "category": NodeCategory.ENTITY,
                "source_system": "perception",
                "logical_step": 1,
                "evidence_ids": ("evidence-1",),
            },
        },
        {
            "op": "add_edge",
            "edge": {
                "edge_id": "edge-1",
                "source_id": "node-a",
                "target_id": "node-b",
                "relation": EdgeRelation.ASSOCIATED_WITH,
                "source_system": "perception",
                "logical_step": 1,
                "evidence_ids": ("evidence-1",),
            },
        },
        {"op": "advance", "logical_step": 2},
    )
    return InMemoryActiveCognitionRuntime.replay(
        policy,
        working_capacity=2,
        operations=operations,
    )


snapshot = build_snapshot()
payload = snapshot.to_dict()
canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
independent_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

checks = {
    "schema_version": payload["schema_version"] == "active_cognition_snapshot.v1",
    "graph_schema_version": payload["graph"]["schema_version"] == "active_cognitive_graph.v1",
    "working_memory_schema_version": payload["working_memory"]["schema_version"] == "working_memory.v1",
    "deterministic_replay_match": independent_digest == snapshot.digest(),
    "expected_digest_match": independent_digest == EXPECTED_DIGEST,
    "cognitive_state_projection": snapshot.to_cognitive_state(
        state_id="verifier-state"
    ).to_dict()["schema_version"]
    == "cognitive_state.v1",
    "no_decision_language_fields": {
        "prompt",
        "reasoning",
        "selected_action",
        "text",
        "reward",
    }.isdisjoint(payload),
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
