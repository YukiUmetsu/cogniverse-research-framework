from typing import Protocol


class ExperimentLifecycle(Protocol):
    def preflight(self) -> dict:
        ...

    def execute(self) -> dict:
        ...

    def analyze(self) -> dict:
        ...

    def settle(self) -> dict:
        ...
