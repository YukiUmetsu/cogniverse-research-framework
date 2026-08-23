#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/evidence \
  src/cogniverse_framework/reporting \
  src/cogniverse_framework/comparison \
  tests \
  scripts

cat > src/cogniverse_framework/evidence/__init__.py <<'PY'
from .run_record import RunRecord
from .store import EvidenceStore

__all__ = [
    "RunRecord",
    "EvidenceStore",
]
PY

cat > src/cogniverse_framework/evidence/run_record.py <<'PY'
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import json


@dataclass
class RunRecord:

    experiment_id: str
    status: str

    def create(self):

        payload = {
            "experiment_id": self.experiment_id,
            "status": self.status,
            "timestamp": datetime.utcnow().isoformat(),
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
        ).encode()

        payload["run_id"] = hashlib.sha256(
            encoded
        ).hexdigest()[:16]

        return payload
PY

cat > src/cogniverse_framework/evidence/store.py <<'PY'
from pathlib import Path
import hashlib
import json


class EvidenceStore:

    def __init__(self, root):

        self.root = Path(root)
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def write(self, name, data):

        path = self.root / name

        path.write_text(
            json.dumps(
                data,
                indent=2,
            )
        )

        return {
            "path": str(path),
            "sha256": hashlib.sha256(
                path.read_bytes()
            ).hexdigest(),
        }
PY

cat > src/cogniverse_framework/comparison/__init__.py <<'PY'
from .runs import compare_runs

__all__ = [
    "compare_runs",
]
PY

cat > src/cogniverse_framework/comparison/runs.py <<'PY'
def compare_runs(left, right):

    changes = []

    keys = set(left) | set(right)

    for key in sorted(keys):

        if left.get(key) != right.get(key):
            changes.append(key)

    return {
        "changed": bool(changes),
        "changed_fields": changes,
    }
PY

cat > src/cogniverse_framework/reporting/research_report.py <<'PY'
from pathlib import Path


def write_research_markdown(path, result):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    content = f"""# Research Report

Experiment: {result.get("experiment")}

Status: {result.get("status")}

## Evidence

{result}
"""

    path.write_text(content)

    return str(path)
PY

cat > tests/test_bundle_10_evidence.py <<'PY'
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
PY

cat > scripts/run_bundle_10.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 10: EVIDENCE AND REPRODUCIBILITY"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

rm -rf .runtime/bundle10

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.evidence import (
    RunRecord,
    EvidenceStore,
)

from cogniverse_framework.comparison import (
    compare_runs,
)

record = RunRecord(
    "exp042",
    "COMPLETE",
).create()

artifact = EvidenceStore(
    ".runtime/bundle10"
).write(
    "run.json",
    record,
)

comparison = compare_runs(
    {"mutation": 1},
    {"mutation": 2},
)

print(json.dumps({
    "bundle": "10",
    "evidence": "PASS",
    "run_id": record["run_id"],
    "hash_created": "sha256" in artifact,
    "comparison": comparison["changed"],
}, indent=2))
PY
SH

chmod +x scripts/run_bundle_10.sh

git add .
git commit -m "Implement Bundle 10 evidence reproducibility system"

echo "Bundle 10 created"
