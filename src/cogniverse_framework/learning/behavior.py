from dataclasses import dataclass, asdict


@dataclass
class BehaviorTrace:

    state: str
    decision: str
    action: str
    result: str

    def to_dict(self):
        return asdict(self)
