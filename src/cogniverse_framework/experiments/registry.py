class ExperimentRegistry:

    def __init__(self):
        self._experiments = {}

    def register(self, adapter):

        self._experiments[
            adapter.experiment_id
        ] = adapter

    def get(self, experiment_id):

        return self._experiments[
            experiment_id
        ]

    def list(self):

        return sorted(
            self._experiments.keys()
        )
