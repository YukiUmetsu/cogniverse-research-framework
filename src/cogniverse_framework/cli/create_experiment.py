import argparse
import json

from cogniverse_framework.generator.generator import (
    ExperimentGenerator,
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "experiment_id"
    )

    parser.add_argument(
        "--type",
        required=True,
        dest="experiment_type",
    )

    args = parser.parse_args()

    result = ExperimentGenerator().generate(
        args.experiment_id,
        args.experiment_type,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
