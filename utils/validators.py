from decimal import Decimal
from typing import Any, Dict
from utils.exceptions import ValidationError


class DataValidator:
    @staticmethod
    def validate_user_data(data: Dict[str, Any]) -> bool:
        if not data.get('username') or len(data['username']) < 3:
            raise ValidationError("Username must be at least 3 characters long")

        if not data.get('email') or '@' not in data['email']:
            raise ValidationError("Invalid email format")

        if not data.get('password_hash'):
            raise ValidationError("Password hash is required")

        return True

    @staticmethod
    def validate_account_data(data: Dict[str, Any]) -> bool:
        valid_types = {'savings', 'checking', 'investment', 'loan'}
        if not data.get('account_type') or data['account_type'] not in valid_types:
            raise ValidationError("Invalid account type")

        if not data.get('user_id'):
            raise ValidationError("User ID is required")

        return True

    @staticmethod
    def validate_transaction_data(data: Dict[str, Any]) -> bool:
        if not data.get('amount') or Decimal(str(data['amount'])) <= 0:
            raise ValidationError("Invalid transaction amount")

        if not data.get('from_account_id'):
            raise ValidationError("Source account is required")

        return True