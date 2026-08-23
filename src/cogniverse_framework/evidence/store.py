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
