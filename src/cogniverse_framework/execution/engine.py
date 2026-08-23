import json

from cogniverse_framework.execution.lifecycle import (
    Lifecycle,
)


class ExecutionEngine:

    def __init__(self, adapter):
        self.adapter = adapter
        self.lifecycle = Lifecycle()

    def run(self):

        preflight = self.lifecycle.preflight()

        execution = self.lifecycle.execute(
            self.adapter
        )

        analysis = self.lifecycle.analyze(
            execution
        )

        settlement = self.lifecycle.settle()

        return {
            "status": "COMPLETE",
            "phases": {
                "preflight": preflight.__dict__,
                "execute": execution.__dict__,
                "analyze": analysis.__dict__,
                "settle": settlement.__dict__,
            },
        }
