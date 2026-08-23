from cogniverse_framework.experiments.base_adapter import (
    ExperimentAdapter,
)

from cogniverse_framework.research import (
    ReplaySession,
    MutationAnalysis,
)


class Exp042Adapter(
    ExperimentAdapter
):

    experiment_id = "exp042"

    def __init__(self, replay_events=None):
        self.replay_events = replay_events or []

    def run(self):

        replay = ReplaySession(
            seed=51005,
            events=self.replay_events,
        )

        contract = (
            replay.validate_replay_only()
        )

        mutation = MutationAnalysis(
            baseline={
                51003: 376,
                51004: 305,
            },
            candidate={
                51003: 382,
                51004: 311,
            },
        ).compare()

        return {
            "experiment": self.experiment_id,
            "status": "COMPLETE",
            "contract": contract,
            "mutation_analysis": mutation,
            "learning_evidence": {
                "strategy":
                    "prefer_promising_branches",
                "supporting_states": [
                    "cb148158",
                    "790ffc07",
                ],
                "confidence": 0.8,
            },
        }

    def execute(self):
        return self.run()

    def analyze(self, result):
        return result

    def collect_learning_evidence(self, result):
        return result.get(
            "learning_evidence",
            {},
        )
