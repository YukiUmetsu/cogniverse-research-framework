class EnvironmentRegistry:

    def __init__(self):
        self.environments = {}

    def register(self, adapter):

        self.environments[
            adapter.environment_id
        ] = adapter

    def get(self, name):

        return self.environments[name]
