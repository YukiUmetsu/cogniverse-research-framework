from cogniverse_framework.experiments.base_adapter import (
    ExperimentAdapter,
)


class Exp042Adapter(
    ExperimentAdapter
):

    experiment_id = "exp042"

    def execute(self):

        return {
            "mutation_found": True,
            "states": [
                "cb148158",
                "790ffc07",
            ],
        }

    def analyze(self, result):

        return {
            "successful_states":
                result["states"],
            "mutation_found":
                result["mutation_found"],
        }

    def collect_learning_evidence(
        self,
        result,
    ):

        return {
            "strategy":
                "prefer_pro        ranches",
            "supporting_states":
                result["successful_states"],
            "confidence":
                0.8,
        }
