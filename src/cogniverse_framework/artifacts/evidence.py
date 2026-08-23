from pathlib import Path
import hashlib


class EvidenceRegistry:

    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def register(self, name, content):
        path = self.directory / name
        path.write_text(content)

        return {
            "file": str(path),
            "sha256": hashlib.sha256(
                path.read_bytes()
            ).hexdigest(),
        }
