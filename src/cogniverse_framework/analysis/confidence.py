def confidence_score(
    successes,
    failures,
):

    total = successes + failures

    if total == 0:
        return 0.0

    return round(
        successes / total,
        3,
    )
