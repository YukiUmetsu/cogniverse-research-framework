class ExperimentRegistry:

    def __init__(self):
        self.experiments = {}

    def register(self, experiment):
        self.experiments[
            experiment.experiment_id
        ] = experiment

    def get(self, experiment_id):
        return self.experiments.get(
            experiment_id
        )
