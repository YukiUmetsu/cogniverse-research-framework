def summarize(result: dict) -> dict:
    return {
        "status": result.get("status"),
        "experiment": result.get("experiment"),
    }
