import json


def write_report(path, result):
    with open(path, "w") as f:
        f.write(json.dumps(result, indent=2))
