import tempfile
import unittest

from cogniverse_framework.integration import (
    ExperimentRunner,
)


class TestBundle09(unittest.TestCase):

    def test_exp042_full_execution(self):

        with tempfile.TemporaryDirectory() as tmp:

            result = ExperimentRunner(
                "exp042"
            ).run(tmp)

            self.assertEqual(
                result["experiment"],
                "exp042",
            )

            self.assertEqual(
                result["result"]["status"],
                "COMPLETE",
            )


if __name__ == "__main__":
    unittest.main()
