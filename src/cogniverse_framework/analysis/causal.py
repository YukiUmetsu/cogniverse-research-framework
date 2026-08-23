def estimate_effect(baseline, intervention):

    return {
        "baseline": baseline,
        "intervention": intervention,
        "effect": round(
            intervention - baseline,
            3,
        ),
    }
