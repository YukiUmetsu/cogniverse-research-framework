import json
from pathlib import Path


def write_research_report(path, result):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            result,
            indent=2,
        )
    )

    return str(path)
