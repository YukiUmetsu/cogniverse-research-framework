class ExampleExperiment:

    def preflight(self):
        return {
            "status": "PASS",
            "environment_reset": False,
        }

    def execute(self):
        return {
            "executed": False,
            "mode": "example",
        }

    def analyze(self):
        return {
            "analysis": "example",
        }

    def settle(self):
        return {
            "settled": True,
        }
