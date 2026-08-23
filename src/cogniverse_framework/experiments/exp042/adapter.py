from cogniverse_framework.research import (
    ReplaySession,
    MutationAnalysis,
)


class Exp042Adapter:

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
            "contract": contract,
            "mutation_analysis": mutation,
        }
