from pathlib import Path
import json
from .hashing import sha256_file


class ArtifactManager:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, name: str, data: dict):
        path = self.output_dir / name
        path.write_text(json.dumps(data, indent=2, sort_keys=True))
        return {
            "path": str(path),
            "sha256": sha256_file(path),
        }
