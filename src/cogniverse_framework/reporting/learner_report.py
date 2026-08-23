from pathlib import Path
import json


def write_learner_report(path, evidence):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            evidence,
            indent=2,
        )
    )

    return str(path)
