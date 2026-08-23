def success_rate(successes, trials):
    if trials == 0:
        return 0.0
    return round(successes / trials, 3)


def confidence_range(successes, trials):
    rate = success_rate(successes, trials)
    margin = round(1.96 * ((rate * (1 - rate) / trials) ** 0.5), 3)

    return {
        "lower": max(0, round(rate - margin, 3)),
        "upper": min(1, round(rate + margin, 3)),
    }
