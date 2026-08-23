from dataclasses import dataclass


@dataclass
class LifecycleResult:
    phase: str
    status: str
    details: dict


class Lifecycle:

    def preflight(self):
        return LifecycleResult(
            "preflight",
            "PASS",
            {
                "environment_reset": False,
            },
        )

    def execute(self, adapter):
        return LifecycleResult(
            "execute",
            "PASS",
            adapter.run(),
        )

    def analyze(self, execution_result):
        return LifecycleResult(
            "analyze",
            "PASS",
            {
                "input_status": execution_result.status,
            },
        )

    def settle(self):
        return LifecycleResult(
            "settle",
            "PASS",
            {
                "settled": True,
            },
        )
