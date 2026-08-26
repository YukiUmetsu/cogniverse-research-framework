import dataclasses
import json
import unittest

from cogniverse_framework.cognition import PerceptModality, PublicPercept


class PublicPerceptTests(unittest.TestCase):
    def make(self, **overrides):
        values = dict(
            percept_id="percept-12",
            modality=PerceptModality.STRUCTURED,
            source_system="public-grid-adapter",
            logical_step=12,
            content_sha256="a" * 64,
            confidence_ppm=None,
            evidence_ids=("event-12", "sensor-2"),
        )
        values.update(overrides)
        return PublicPercept(**values)

    def test_is_immutable_and_deterministic(self):
        first = self.make(evidence_ids=("sensor-2", "event-12"))
        second = self.make()
        self.assertEqual(first.canonical_json(), second.canonical_json())
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(json.loads(first.canonical_json()), first.to_dict())
        with self.assertRaises(dataclasses.FrozenInstanceError):
            first.logical_step = 13

    def test_keeps_unknown_confidence_explicit(self):
        payload = self.make(confidence_ppm=None).to_dict()
        self.assertIsNone(payload["confidence_ppm"])
        self.assertEqual(payload["schema_version"], "public_percept.v1")

    def test_requires_public_provenance_and_content_identity(self):
        with self.assertRaisesRegex(ValueError, "evidence_ids"):
            self.make(evidence_ids=())
        with self.assertRaisesRegex(ValueError, "content_sha256"):
            self.make(content_sha256="not-a-digest")

    def test_rejects_forbidden_information_and_invalid_confidence(self):
        with self.assertRaisesRegex(ValueError, "forbidden marker"):
            self.make(evidence_ids=("future-outcome",))
        with self.assertRaisesRegex(ValueError, "confidence_ppm"):
            self.make(confidence_ppm=1_000_001)

    def test_rejects_duplicate_provenance_and_noncanonical_digest(self):
        with self.assertRaisesRegex(ValueError, "unique identifiers"):
            self.make(evidence_ids=("event-12", "event-12"))
        with self.assertRaisesRegex(ValueError, "content_sha256"):
            self.make(content_sha256="A" * 64)

    def test_has_no_decision_or_language_control_fields(self):
        payload = self.make().to_dict()
        self.assertTrue({"text", "prompt", "reasoning", "reward", "selected_action", "belief"}.isdisjoint(payload))


if __name__ == "__main__":
    unittest.main()
