from cogniverse_framework.analysis import (
    compare_knowledge,
)


class EvidenceCollector:

    def collect(self, learner_run):

        delta = compare_knowledge(
            learner_run.before,
            learner_run.after,
        )

        return {
            "experiment": learner_run.experiment_id,
            "behavior_change": delta,
            "traces": learner_run.traces,
        }
