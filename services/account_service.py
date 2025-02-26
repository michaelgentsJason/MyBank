from typing import Optional, Dict
from dal.repositories.account_repository import AccountRepository
from security.encryption import EncryptionService
from utils.exceptions import ValidationError
from utils.logger import bank_logger
from decimal import Decimal



class AccountService:
    def __init__(self,
                 account_repository: AccountRepository,
                 encryption_service: EncryptionService):
        self.account_repository = account_repository
        self.encryption_service = encryption_service

    async def create_account(self, user_id: int, account_type: str) -> dict:
        """创建新账户"""
        try:
            # 生成账户号码
            account_number = self._generate_account_number()

            account_data = {
                "user_id": user_id,
                "account_type": account_type,
                "account_number": account_number,
                "balance": 0.0,
                "status": "active"
            }

            account = self.account_repository.create(account_data)
            return {
                "account_id": account.account_id,
                "account_number": account.account_number,
                "account_type": account.account_type,
                "balance": float(account.balance),
                "status": account.status
            }

        except Exception as e:
            bank_logger.error(f"Failed to create account: {str(e)}")
            raise

    async def get_account_balance(self, account_id: int) -> float:
        """获取账户余额"""
        try:
            account = self.account_repository.get_by_id(account_id)
            if not account:
                raise ValidationError("Account not found")

            return account.balance

        except Exception as e:
            bank_logger.error(f"Failed to get balance: {str(e)}")
            raise

    async def get_account_by_id(self, account_id: int) -> Optional[dict]:
        """获取账户详情"""
        try:
            account = self.account_repository.get_by_id(account_id)
            if not account:
                return None

            return {
                "account_id": account.account_id,
                "account_number": account.account_number,
                "account_type": account.account_type,
                "balance": float(account.balance),
                "status": account.status
            }
        except Exception as e:
            bank_logger.error(f"Failed to get account: {str(e)}")
            raise

    async def deposit(self, account_id: int, amount: Decimal) -> Dict:
        """向账户存款"""
        try:
            if amount <= 0:
                raise ValidationError("Deposit amount must be positive")

            # 获取账户
            account = self.account_repository.get_by_id(account_id)
            if not account:
                raise ValidationError("Account not found")

            if account.status != 'active':
                raise ValidationError("Account is not active")

            # 更新余额
            updated_account = self.account_repository.update_balance(account_id, amount)

            return {
                "account_id": updated_account.account_id,
                "account_number": updated_account.account_number,
                "account_type": updated_account.account_type,
                "balance": float(updated_account.balance),
                "status": updated_account.status
            }
        except Exception as e:
            bank_logger.error(f"Deposit failed: {str(e)}")
            raise

    def _generate_account_number(self) -> str:
        """生成唯一的账户号码"""
        # 实现账户号码生成逻辑
        import random
        return f"ACC{random.randint(10000, 99999)}"