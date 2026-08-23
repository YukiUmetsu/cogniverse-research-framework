class BehaviorExtractor:

    def extract(self, trajectory):

        actions = trajectory.successful_actions()

        if "continue_branch" in actions:

            return {
                "strategy":
                    "prefer_promising_branches",
                "reason":
                    "successful continuation after exploration",
                "evidence_states":
                    trajectory.states(),
                "confidence":
                    0.74,
            }

        return {
            "strategy": "unknown",
            "reason": "insufficient evidence",
            "evidence_states":
                trajectory.states(),
            "confidence": 0.0,
        }
