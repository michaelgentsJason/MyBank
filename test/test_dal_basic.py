import unittest
from config.database import SessionLocal
from dal.repositories.user_repository import UserRepository
from dal.repositories.account_repository import AccountRepository
from dal.repositories.transaction_repository import TransactionRepository

class TestDALBasic(unittest.TestCase):
    def setUp(self):
        """测试开始前，初始化数据库会话及各仓储实例"""
        self.db = SessionLocal()
        self.user_repo = UserRepository(self.db)
        self.account_repo = AccountRepository(self.db)
        self.transaction_repo = TransactionRepository(self.db)

    def tearDown(self):
        """测试结束后提交事务并关闭会话"""
        self.db.commit()
        self.db.close()

    def test_user_crud(self):
        """测试用户的创建、查询、更新与删除"""
        # 创建用户
        user_data = {
            "username": "test_user",
            "password_hash": "test_hash",
            "email": "test_user@example.com",
            "status": "active"
        }
        user = self.user_repo.create(user_data)
        self.assertIsNotNone(user)
        self.assertIsNotNone(user.user_id)

        # 查询用户
        queried_user = self.user_repo.get_by_username("test_user")
        self.assertIsNotNone(queried_user)
        self.assertEqual(queried_user.user_id, user.user_id)

        # 更新用户（例如更新邮箱）
        updated_user = self.user_repo.update(user.user_id, {"email": "updated@example.com"})
        self.assertEqual(updated_user.email, "updated@example.com")

        # 删除用户
        delete_result = self.user_repo.delete(user.user_id)
        self.assertTrue(delete_result)
        self.assertIsNone(self.user_repo.get_by_username("test_user"))

    def test_account_crud(self):
        """测试账户的创建、查询、余额更新与删除"""
        # 先创建一个用户，因为账户需要关联用户
        user_data = {
            "username": "account_test_user",
            "password_hash": "hash",
            "email": "account_test@example.com",
            "status": "active"
        }
        user = self.user_repo.create(user_data)

        # 创建账户
        account_data = {
            "user_id": user.user_id,
            "account_type": "savings",
            "account_number": "ACC123456",
            "balance": 1000.00,
            "status": "active"
        }
        account = self.account_repo.create(account_data)
        self.assertIsNotNone(account)
        self.assertIsNotNone(account.account_id)

        # 查询账户
        queried_account = self.account_repo.get_by_account_number("ACC123456")
        self.assertIsNotNone(queried_account)
        self.assertEqual(queried_account.account_id, account.account_id)

        # 更新账户余额（增加500元）
        updated_account = self.account_repo.update_balance(account.account_id, 500.0)
        self.assertAlmostEqual(float(updated_account.balance), 1500.00, places=2)

        # 删除账户
        delete_result = self.account_repo.delete(account.account_id)
        self.assertTrue(delete_result)

        # 清理：删除用户
        self.user_repo.delete(user.user_id)

    def test_transaction_crud(self):
        """测试交易的创建、查询与删除"""
        # 创建一个用户和两个账户（转账需要两个账户）
        user_data = {
            "username": "transaction_user",
            "password_hash": "hash",
            "email": "transaction_user@example.com",
            "status": "active"
        }
        user = self.user_repo.create(user_data)

        account_data1 = {
            "user_id": user.user_id,
            "account_type": "checking",
            "account_number": "ACC111111",
            "balance": 2000.00,
            "status": "active"
        }
        account_data2 = {
            "user_id": user.user_id,
            "account_type": "checking",
            "account_number": "ACC222222",
            "balance": 3000.00,
            "status": "active"
        }
        account1 = self.account_repo.create(account_data1)
        account2 = self.account_repo.create(account_data2)

        # 创建交易记录（例如转账500元）
        transaction_data = {
            "from_account_id": account1.account_id,
            "to_account_id": account2.account_id,
            "amount": 500.00,
            "transaction_type": "transfer",
            "status": "pending"  # 或 "completed" 根据业务需求
        }
        transaction = self.transaction_repo.create(transaction_data)
        self.assertIsNotNone(transaction)
        self.assertIsNotNone(transaction.transaction_id)

        # 查询与账户相关的交易记录
        transactions_for_account1 = self.transaction_repo.get_account_transactions(account1.account_id)
        self.assertTrue(len(transactions_for_account1) >= 1)

        # 删除交易记录
        delete_result = self.transaction_repo.delete(transaction.transaction_id)
        self.assertTrue(delete_result)

        # 清理：删除账户和用户
        self.account_repo.delete(account1.account_id)
        self.account_repo.delete(account2.account_id)
        self.user_repo.delete(user.user_id)

if __name__ == "__main__":
    unittest.main()
