import unittest

from cogniverse_framework.contracts.audit_contract import AuditContract


class TestBundle03(unittest.TestCase):

    def test_contract(self):
        result = AuditContract().validate()
        self.assertTrue(result["validated"])


if __name__ == "__main__":
    unittest.main()
