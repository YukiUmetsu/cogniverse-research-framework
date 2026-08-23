import tempfile
import unittest

from cogniverse_framework.evidence import (
    RunRecord,
    EvidenceStore,
)

from cogniverse_framework.comparison import (
    compare_runs,
)


class TestBundle10(unittest.TestCase):

    def test_run_record(self):

        result = RunRecord(
            "exp042",
            "COMPLETE",
        ).create()

        self.assertIn(
            "run_id",
            result,
        )

    def test_evidence_hash(self):

        with tempfile.TemporaryDirectory() as tmp:

            result = EvidenceStore(
                tmp
            ).write(
                "result.json",
                {"ok": True},
            )

            self.assertIn(
                "sha256",
                result,
            )

    def test_compare(self):

        result = compare_runs(
            {"a": 1},
            {"a": 2},
        )

        self.assertTrue(
            result["changed"]
        )


if __name__ == "__main__":
    unittest.main()
