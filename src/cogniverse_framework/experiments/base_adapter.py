from abc import ABC, abstractmethod


class ExperimentAdapter(ABC):

    experiment_id = None

    def preflight(self):
        return {
            "status": "PASS"
        }

    @abstractmethod
    def execute(self):
        pass

    def analyze(self, result):
        return result

    def collect_learning_evidence(self, result):
        return {}

    def run(self):

        preflight = self.preflight()

        execution = self.execute()

        analysis = self.analyze(
            execution
        )

        evidence = (
            self.collect_learning_evidence(
                analysis
            )
        )

        return {
            "preflight": preflight,
            "execution": execution,
            "analysis": analysis,
            "learning_evidence": evidence,
        }
