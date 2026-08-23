def compare_runs(left, right):

    changes = []

    keys = set(left) | set(right)

    for key in sorted(keys):

        if left.get(key) != right.get(key):
            changes.append(key)

    return {
        "changed": bool(changes),
        "changed_fields": changes,
    }
