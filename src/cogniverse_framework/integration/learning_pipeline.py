from cogniverse_framework.learning.learner_run import (
    LearnerRun,
)

from cogniverse_framework.learning.evidence_collector import (
    EvidenceCollector,
)


class LearningPipeline:

    def __init__(self, experiment_id):
        self.experiment_id = experiment_id

    def run(self):

        learner = LearnerRun(
            experiment_id=self.experiment_id,
            before={
                "concepts": [],
                "strategies": [
                    "random_exploration"
                ],
            },
            after={
                "concepts": [
                    "frontier_value"
                ],
                "strategies": [
                    "information_guided_exploration"
                ],
            },
            traces=[
                {
                    "state": "ef562c19",
                    "decision": "continue_branch",
                    "reason": "future_value",
                }
            ],
        )

        return EvidenceCollector().collect(
            learner
        )
