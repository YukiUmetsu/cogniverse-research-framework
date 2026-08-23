def compare_ablation(enabled, disabled):

    return {
        "enabled": enabled,
        "disabled": disabled,
        "difference": round(
            enabled - disabled,
            3,
        ),
    }
