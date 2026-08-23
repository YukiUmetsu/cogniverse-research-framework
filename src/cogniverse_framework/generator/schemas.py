VALID_TYPES = {
    "replay-analysis",
    "audit",
    "simulation",
}


def validate_experiment_id(experiment_id):
    if not experiment_id:
        raise ValueError("experiment_id is required")

    allowed = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789-_"
    )

    if not set(experiment_id) <= allowed:
        raise ValueError(
            "experiment_id contains invalid characters"
        )


def validate_type(experiment_type):
    if experiment_type not in VALID_TYPES:
        raise ValueError(
            f"unsupported experiment type: {experiment_type}"
        )
