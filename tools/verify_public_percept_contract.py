"""Independent, dependency-free verification of the PublicPercept v1 fixture."""

from __future__ import annotations

import hashlib
import json

from cogniverse_framework.cognition import PerceptModality, PublicPercept


def verify() -> dict[str, bool | str]:
    percept = PublicPercept(
        percept_id="percept-12",
        modality=PerceptModality.STRUCTURED,
        source_system="public-grid-adapter",
        logical_step=12,
        content_sha256="a" * 64,
        confidence_ppm=None,
        evidence_ids=("sensor-2", "event-12"),
    )
    payload = percept.to_dict()
    independently_serialized = json.dumps(
        {
            "confidence_ppm": None,
            "content_sha256": "a" * 64,
            "evidence_ids": ["event-12", "sensor-2"],
            "logical_step": 12,
            "modality": "structured",
            "percept_id": "percept-12",
            "schema_version": "public_percept.v1",
            "source_system": "public-grid-adapter",
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    checks = {
        "schema_exact": payload["schema_version"] == "public_percept.v1",
        "canonical_json_exact": percept.canonical_json() == independently_serialized,
        "digest_exact": percept.digest()
        == hashlib.sha256(independently_serialized.encode("utf-8")).hexdigest(),
        "unknown_confidence_preserved": payload["confidence_ppm"] is None,
        "provenance_normalized": payload["evidence_ids"] == ["event-12", "sensor-2"],
        "no_decision_fields": {"reward", "selected_action", "prompt", "reasoning"}.isdisjoint(payload),
        "no_raw_payload": {"text", "bytes", "payload", "observation"}.isdisjoint(payload),
    }
    return {**checks, "canonical_digest": percept.digest()}


if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all(value is True for key, value in result.items() if key != "canonical_digest"):
        raise SystemExit(1)
