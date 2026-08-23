from dataclasses import dataclass, field


@dataclass
class LearnerRun:

    experiment_id: str
    before: dict
    after: dict
    traces: list = field(default_factory=list)

    def snapshot(self):

        return {
            "experiment": self.experiment_id,
            "before": self.before,
            "after": self.after,
            "traces": self.traces,
        }
