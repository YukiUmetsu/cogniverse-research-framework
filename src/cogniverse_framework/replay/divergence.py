def first_divergence(left, right):
    length = min(len(left), len(right))

    for i in range(length):
        if left[i] != right[i]:
            return {
                "index": i,
                "left": left[i],
                "right": right[i],
            }

    if len(left) != len(right):
        return {
            "index": length,
            "type": "length_difference",
        }

    return None
