from pathlib import Path
import hashlib
import json


def write_execution_manifest(directory, result):

    directory = Path(directory)

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = directory / "execution.json"

    output.write_text(
        json.dumps(result, indent=2)
    )

    return {
        "path": str(output),
        "sha256": hashlib.sha256(
            output.read_bytes()
        ).hexdigest(),
    }
