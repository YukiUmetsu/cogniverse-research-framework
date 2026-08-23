def compare_seed_matrix(baseline, candidate):
    rows = []

    for seed in sorted(
        set(baseline.keys()) | set(candidate.keys())
    ):
        rows.append({
            "seed": seed,
            "baseline": baseline.get(seed),
            "candidate": candidate.get(seed),
            "changed": (
                baseline.get(seed)
                != candidate.get(seed)
            ),
        })

    return rows
