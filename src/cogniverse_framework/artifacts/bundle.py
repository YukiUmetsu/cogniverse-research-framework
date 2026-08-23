from pathlib import Path
import json
import hashlib


class ArtifactBundle:

    def __init__(self, path):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)

    def write_json(self, name, data):
        target = self.path / name
        target.write_text(json.dumps(data, indent=2))

        return {
            "file": str(target),
            "sha256": hashlib.sha256(
                target.read_bytes()
            ).hexdigest(),
        }
