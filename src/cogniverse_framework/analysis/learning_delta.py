def compare_knowledge(before, after):

    before_concepts = set(
        before.get("concepts", [])
    )

    after_concepts = set(
        after.get("concepts", [])
    )

    before_strategies = set(
        before.get("strategies", [])
    )

    after_strategies = set(
        after.get("strategies", [])
    )

    return {
        "new_concepts": sorted(
            after_concepts - before_concepts
        ),
        "removed_concepts": sorted(
            before_concepts - after_concepts
        ),
        "new_strategies": sorted(
            after_strategies - before_strategies
        ),
        "removed_strategies": sorted(
            before_strategies - after_strategies
        ),
    }
