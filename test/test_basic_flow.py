import unittest
import asyncio
from config.database import get_db
from security.encryption import EncryptionService
from security.key_manager import KeyManager
from security.security_utils import SecurityUtils
from services.user_service import UserService
from services.account_service import AccountService
from services.transaction_service import TransactionService
from dal.repositories.user_repository import UserRepository
from dal.repositories.account_repository import AccountRepository
from dal.repositories.transaction_repository import TransactionRepository
from dal.repositories.encryption_keys import EncryptionKeyRepository


class TestBankSystem(unittest.TestCase):
    def setUp(self):
        """测试开始前的设置"""
        self.db = next(get_db())

        # 初始化仓储
        self.key_repository = EncryptionKeyRepository(self.db)
        self.user_repository = UserRepository(self.db)
        self.account_repository = AccountRepository(self.db)
        self.transaction_repository = TransactionRepository(self.db)

        # 初始化安全服务
        self.key_manager = KeyManager(self.key_repository)
        self.security_utils = SecurityUtils("your-secret-key")
        self.encryption_service = EncryptionService(self.key_manager)

        # 初始化业务服务
        self.user_service = UserService(
            self.user_repository,
            self.security_utils,
            self.encryption_service
        )
        self.account_service = AccountService(
            self.account_repository,
            self.encryption_service
        )

    def tearDown(self):
        """测试结束后的清理"""
        self.db.close()

    def test_user_registration(self):
        """测试用户注册"""

        async def run_test():
            user_result = await self.user_service.create_user(
                username="test_user",
                password="test_password",
                email="test@example.com"
            )
            self.assertIsNotNone(user_result)
            self.assertIn("user_id", user_result)
            self.assertIn("token", user_result)
            return user_result

        return asyncio.run(run_test())

    def test_account_creation(self):
        """测试账户创建"""

        async def run_test():
            # 先创建用户
            user_result = await self.user_service.create_user(
                username="test_user2",
                password="test_password",
                email="test2@example.com"
            )

            # 创建账户
            account_result = await self.account_service.create_account(
                user_id=user_result["user_id"],
                account_type="savings"
            )

            self.assertIsNotNone(account_result)
            self.assertIn("account_id", account_result)
            self.assertIn("account_number", account_result)
            return account_result

        return asyncio.run(run_test())

    def test_user_info_retrieval(self):
        """测试获取用户信息"""

        async def run_test():
            # 创建用户
            user_result = await self.user_service.create_user(
                username="test_user3",
                password="test_password",
                email="test3@example.com"
            )

            # 获取用户信息
            user_info = await self.user_service.get_user_info(user_result["user_id"])

            self.assertIsNotNone(user_info)
            self.assertEqual(user_info["username"], "test_user3")
            self.assertEqual(user_info["email"], "test3@example.com")
            return user_info

        return asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()