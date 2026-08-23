from dataclasses import dataclass, field


@dataclass
class Trajectory:

    transitions: list = field(
        default_factory=list
    )

    def add(self, transition):
        self.transitions.append(
            transition
        )

    def states(self):

        return [
            t.state
            for t in self.transitions
        ]

    def successful_actions(self):

        return [
            t.action
            for t in self.transitions
            if t.outcome == "success"
        ]
