import unittest
from pathlib import Path
import tempfile

from cogniverse_framework.generator.generator import (
    ExperimentGenerator,
)


class TestGenerator(unittest.TestCase):

    def test_generate(self):

        with tempfile.TemporaryDirectory() as tmp:

            result = ExperimentGenerator(
                tmp
            ).generate(
                "exp043",
                "replay-analysis",
            )

            path = Path(
                result["path"]
            )

            self.assertTrue(
                (path / "manifest.yaml").exists()
            )

            self.assertTrue(
                (path / "adapter.py").exists()
            )

            self.assertTrue(
                (path / "generation.json").exists()
            )


if __name__ == "__main__":
    unittest.main()
