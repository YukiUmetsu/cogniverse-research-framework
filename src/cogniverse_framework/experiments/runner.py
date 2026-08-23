from .execution_result import ExecutionResult


class ExperimentRunner:

    def __init__(self, experiment_id, lifecycle):
        self.experiment_id = experiment_id
        self.lifecycle = lifecycle

    def run(self):
        result = ExecutionResult(
            experiment_id=self.experiment_id,
            status="RUNNING",
        )

        result.phase_results["preflight"] = (
            self.lifecycle.preflight()
        )

        result.phase_results["execute"] = (
            self.lifecycle.execute()
        )

        result.phase_results["analyze"] = (
            self.lifecycle.analyze()
        )

        result.phase_results["settle"] = (
            self.lifecycle.settle()
        )

        result.status = "COMPLETE"

        return result
