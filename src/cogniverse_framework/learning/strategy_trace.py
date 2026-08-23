from dataclasses import dataclass, asdict


@dataclass
class StrategyTrace:

    strategy: str
    reason: str
    confidence: float

    def to_dict(self):
        return asdict(self)
