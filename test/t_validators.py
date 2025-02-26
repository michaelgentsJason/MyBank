import unittest
from utils.validators import DataValidator
from utils.exceptions import ValidationError
from decimal import Decimal


class TestValidators(unittest.TestCase):

    def test_validate_user_data_success(self):
        data = {
            "username": "alice",
            "password_hash": "hash_value",
            "email": "alice@example.com"
        }
        self.assertTrue(DataValidator.validate_user_data(data))

    def test_validate_user_data_failure_username(self):
        data = {
            "username": "al",
            "password_hash": "hash_value",
            "email": "alice@example.com"
        }
        with self.assertRaises(ValidationError):
            DataValidator.validate_user_data(data)

    def test_validate_user_data_failure_email(self):
        data = {
            "username": "alice",
            "password_hash": "hash_value",
            "email": "aliceexample.com"
        }
        with self.assertRaises(ValidationError):
            DataValidator.validate_user_data(data)

    def test_validate_account_data_success(self):
        data = {
            "account_type": "savings",
            "user_id": 1
        }
        self.assertTrue(DataValidator.validate_account_data(data))

    def test_validate_account_data_failure(self):
        data = {
            "account_type": "unknown",
            "user_id": 1
        }
        with self.assertRaises(ValidationError):
            DataValidator.validate_account_data(data)

    def test_validate_transaction_data_success(self):
        data = {
            "amount": 100.00,
            "from_account_id": 1
        }
        self.assertTrue(DataValidator.validate_transaction_data(data))

    def test_validate_transaction_data_failure(self):
        data = {
            "amount": 0,
            "from_account_id": 1
        }
        with self.assertRaises(ValidationError):
            DataValidator.validate_transaction_data(data)


if __name__ == "__main__":
    unittest.main()
