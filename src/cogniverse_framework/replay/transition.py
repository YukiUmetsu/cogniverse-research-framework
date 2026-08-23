from dataclasses import dataclass, asdict


@dataclass
class Transition:

    state: str
    action: str
    outcome: str

    def to_dict(self):
        return asdict(self)
