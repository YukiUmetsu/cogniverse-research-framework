from pathlib import Path


def load_manifest(path):
    data = {}

    current = None

    for line in Path(path).read_text().splitlines():
        line = line.strip()

        if not line:
            continue

        if not line.startswith("-") and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if value:
                data[key] = value
            else:
                current = key
                data[current] = {}

    return data
