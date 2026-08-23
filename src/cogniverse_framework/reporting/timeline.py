def build_timeline(events):

    return [
        {
            "step": index,
            "event": event,
        }
        for index, event in enumerate(events)
    ]
