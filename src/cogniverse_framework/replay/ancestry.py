def shared_ancestry(left, right):
    shared = []

    for a, b in zip(left, right):
        if a != b:
            break
        shared.append(a)

    return {
        "shared_length": len(shared),
        "shared_states": shared,
    }
