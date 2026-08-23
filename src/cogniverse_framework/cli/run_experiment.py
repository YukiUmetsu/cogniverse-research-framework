import argparse
import json

from cogniverse_framework.execution.engine import (
    ExecutionEngine,
)


class ExampleAdapter:

    def run(self):

        return {
            "experiment": "generated",
            "result": "ok",
        }


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "manifest"
    )

    args = parser.parse_args()

    result = ExecutionEngine(
        ExampleAdapter()
    ).run()

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
