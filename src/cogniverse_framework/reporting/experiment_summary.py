import json


def write_summary(path, result):
    with open(path, "w") as f:
        json.dump(
            result,
            f,
            indent=2,
        )
