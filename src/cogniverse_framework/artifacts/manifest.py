from pathlib import Path
import hashlib
import json


def create_artifact_manifest(directory):

    directory = Path(directory)

    files = {}

    for path in directory.rglob("*"):
        if path.is_file():
            files[str(path)] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()

    result = {
        "artifact_directory": str(directory),
        "files": files,
    }

    output = directory / "artifact_manifest.json"

    output.write_text(
        json.dumps(result, indent=2)
    )

    return result
