import argparse
import json

from cogniverse_framework.integration import (
    ExperimentRunner,
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "experiment_id"
    )

    parser.add_argument(
        "--artifacts",
        default=".runtime/experiment",
    )

    args = parser.parse_args()

    result = ExperimentRunner(
        args.experiment_id
    ).run(
        args.artifacts
    )

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
