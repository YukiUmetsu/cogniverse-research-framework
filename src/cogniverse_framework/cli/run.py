from cogniverse_framework.experiments.runner import ExperimentRunner
from cogniverse_framework.experiments.example import ExampleExperiment
import json


def main():
    runner = ExperimentRunner(
        "example-exp",
        ExampleExperiment(),
    )

    print(json.dumps(
        runner.run().to_dict(),
        indent=2,
    ))


if __name__ == "__main__":
    main()
