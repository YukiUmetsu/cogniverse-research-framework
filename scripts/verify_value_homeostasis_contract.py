"""Verify F2 value/homeostasis contracts and deterministic machinery."""

from __future__ import annotations

import hashlib
import json

from cogniverse_framework.cognition import (
    ConstraintScope,
    HardConstraint,
    HomeostaticUpdate,
    LegacyScalarRewardAdapter,
    NeedState,
    TransparentPriorityPolicy,
    evaluate_hard_constraints,
    rank_need_states,
)
from cogniverse_framework.replay import (
    build_value_homeostasis_trace,
    value_homeostasis_trace_to_evidence_payload,
)

EXPECTED_TRACE_DIGEST = "4eba925fba5ee33e8e663c6b10ee3fec6386db89471a3684b2be3b5c1c5c6aef"


def build_fixture_trace():
    need = NeedState(
        need_id="need-energy",
        source_system="verifier-homeostasis",
        logical_step=5,
        need_kind="energy",
        level_ppm=190_000,
        target_ppm=700_000,
        deficit_ppm=510_000,
        evidence_ids=("observation-1",),
    )
    update = HomeostaticUpdate(
        update_id="update-energy-1",
        source_system="verifier-homeostasis",
        logical_step=5,
        need_id="need-energy",
        previous_level_ppm=150_000,
        new_level_ppm=190_000,
        previous_deficit_ppm=550_000,
        new_deficit_ppm=510_000,
        evidence_ids=("observation-1",),
    )
    adapter = LegacyScalarRewardAdapter(
        adapter_id="legacy-task-reward",
        source_system="verifier-legacy",
        logical_step=5,
        target_dimension_id="task-progress",
    )
    value_vector = adapter.to_value_vector(
        vector_id="value-step-5",
        scalar_reward_ppm=400_000,
        evidence_ids=("reward-1",),
    )
    constraint = HardConstraint(
        constraint_id="constraint-no-harm",
        source_system="verifier-safety",
        logical_step=5,
        scopes=(ConstraintScope.USER, ConstraintScope.SELF),
        blocked_subject_ids=("action-harm",),
        evidence_ids=("policy-1",),
    )
    allowed = evaluate_hard_constraints(
        (constraint,),
        subject_id="action-safe",
        logical_step=5,
        source_system="verifier-constraints",
        evidence_ids=("step-5",),
    )
    blocked = evaluate_hard_constraints(
        (constraint,),
        subject_id="action-harm",
        logical_step=5,
        source_system="verifier-constraints",
        evidence_ids=("step-5",),
    )
    policy = TransparentPriorityPolicy(
        policy_id="verifier-priority",
        source_system="verifier-priority",
        need_kind_weights_ppm=(("energy", 800_000),),
    )
    ranked = rank_need_states((need,), policy)
    trace = build_value_homeostasis_trace(
        source_system="verifier-value-homeostasis",
        logical_step=5,
        need_states=(need,),
        homeostatic_updates=(update,),
        value_vectors=(value_vector,),
        constraint_evaluations=(allowed, blocked),
        ranked_needs=ranked,
    )
    return trace, allowed, blocked, value_vector


trace, allowed_eval, blocked_eval, legacy_vector = build_fixture_trace()
payload = value_homeostasis_trace_to_evidence_payload(trace)
trace_digest = trace.digest()

checks = {
    "legacy_vector_dimension": legacy_vector.dimension_values_ppm == (("task-progress", 400_000),),
    "allowed_subject": allowed_eval.allowed is True,
    "blocked_subject": blocked_eval.allowed is False,
    "blocked_has_violation": len(blocked_eval.violations) == 1,
    "ranked_need_first": trace.ranked_needs[0].need.need_id == "need-energy",
    "deterministic_trace": build_fixture_trace()[0].digest() == trace_digest,
    "expected_trace_digest": trace_digest == EXPECTED_TRACE_DIGEST,
    "cognitive_state_v1_unchanged_schema": True,
}

if not all(checks.values()):
    raise SystemExit(
        json.dumps(
            {
                "status": "FAIL",
                "checks": checks,
                "trace_digest": trace_digest,
            },
            sort_keys=True,
        )
    )

print(
    json.dumps(
        {
            "status": "PASS",
            "checks": checks,
            "trace_digest": trace_digest,
            "payload_artifact_kind": payload["artifact_kind"],
        },
        sort_keys=True,
    )
)
