def validate_contract(contract: dict) -> dict:
    required = [
        "fresh_seed_block_opened",
        "heldout_seed_block_opened",
        "minigrid_reset_or_step_called",
    ]

    failures = [
        key for key in required
        if contract.get(key) is True
    ]

    return {
        "validated": len(failures) == 0,
        "failures": failures,
    }
