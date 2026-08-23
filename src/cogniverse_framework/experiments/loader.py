from pathlib import Path


def load_experiment(path):

    path = Path(path)

    result = {}

    for line in path.read_text().splitlines():

        if ":" not in line:
            continue

        key, value = line.split(
            ":",
            1,
        )

        result[key.strip()] = value.strip()

    return result
