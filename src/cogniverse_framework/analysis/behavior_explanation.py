def explain_behavior(evidence):

    return {
        "explanation": (
            "The learner repeatedly continued "
            "branches that produced useful outcomes."
        ),
        "strategy": evidence["strategy"],
        "confidence": evidence["confidence"],
    }
