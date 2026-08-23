import tempfile
import unittest

from pathlib import Path

from cogniverse_framework.generator.generator import (
    ExperimentGenerator,
)


class TestBundle07(unittest.TestCase):

    def test_generated_experiment(self):

        with tempfile.TemporaryDirectory() as tmp:

            result = ExperimentGenerator(
                tmp
            ).generate(
                "exp043",
                "replay-analysis",
            )

            root = Path(
                result["path"]
            )

            self.assertTrue(
                (root / "adapter.py").exists()
            )

            self.assertTrue(
                (root / "run.sh").exists()
            )


if __name__ == "__main__":
    unittest.main()
