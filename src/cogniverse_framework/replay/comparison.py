def compare_runs(baseline, candidate):
    return {
        "baseline": baseline,
        "candidate": candidate,
        "changed": baseline != candidate,
    }
