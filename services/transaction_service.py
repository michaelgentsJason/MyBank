from decimal import Decimal
from typing import List, Dict, Optional
from dal.repositories.transaction_repository import TransactionRepository
from dal.repositories.account_repository import AccountRepository
from security.encryption import EncryptionService
from security.signature import SignatureService
from utils.exceptions import ValidationError, InsufficientFundsError
from utils.logger import bank_logger
from datetime import datetime

class TransactionService:
    def __init__(self,
                 transaction_repository: TransactionRepository,
                 account_repository: AccountRepository,
                 encryption_service: EncryptionService,
                 signature_service: Optional[SignatureService] = None):
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository
        self.encryption_service = encryption_service
        self.signature_service = signature_service

    def sign_transaction(self, transaction_data: dict) -> str:
        """
        对交易数据进行签名
        :param transaction_data: 交易数据
        :return: 签名
        """
        # 创建要签名的数据字符串
        signature_data = f"{transaction_data['from_account_id']}|{transaction_data['to_account_id']}|{transaction_data['amount']}|{transaction_data.get('created_at', datetime.utcnow().isoformat())}"

        # 使用SignatureService生成签名
        signature_service = SignatureService("your-secret-key-for-signatures")
        return signature_service.generate_signature(signature_data)

    def verify_transaction_signature(self, transaction_data: dict, signature: str) -> bool:
        """
        验证交易签名
        :param transaction_data: 交易数据
        :param signature: 签名
        :return: 签名是否有效
        """
        # 创建要验证的数据字符串
        signature_data = f"{transaction_data['from_account_id']}|{transaction_data['to_account_id']}|{transaction_data['amount']}|{transaction_data.get('created_at')}"

        # 验证签名
        signature_service = SignatureService("your-secret-key-for-signatures")
        return signature_service.verify_signature(signature_data, signature)

    async def create_transaction(self,
                                 from_account_id: int,
                                 to_account_id: int,
                                 amount: Decimal,
                                 description: str = None) -> Dict:
        """创建新交易"""
        try:
            # 验证账户
            from_account = self.account_repository.get_by_id(from_account_id)
            to_account = self.account_repository.get_by_id(to_account_id)

            if not from_account or not to_account:
                raise ValidationError("Account not found")

            # 检查余额
            if from_account.balance < amount:
                raise InsufficientFundsError("Insufficient funds")

            # 加密交易描述（如果有）
            encrypted_description = None
            if description:
                encrypted_description = self.encryption_service.encrypt_data(description)

            # 创建交易数据
            transaction_data = {
                "from_account_id": from_account_id,
                "to_account_id": to_account_id,
                "amount": amount,
                "transaction_type": "transfer",
                "status": "pending",
                "description": encrypted_description
            }

            # 生成交易签名
            signature = self.sign_transaction(transaction_data)
            transaction_data["signature"] = signature

            # 保存交易
            transaction = self.transaction_repository.create(transaction_data)

            # 更新账户余额
            self.account_repository.update_balance(from_account_id, -amount)
            self.account_repository.update_balance(to_account_id, amount)

            # 更新交易状态
            self.transaction_repository.update(
                transaction.transaction_id,
                {"status": "completed"}
            )

            return {
                "transaction_id": transaction.transaction_id,
                "from_account_id": transaction.from_account_id,
                "to_account_id": transaction.to_account_id,
                "amount": float(transaction.amount),
                "type": transaction.transaction_type,
                "status": "completed",
                "created_at": transaction.created_at,
                "description": description if description else None
            }

        except Exception as e:
            bank_logger.error(f"Transaction failed: {str(e)}")
            raise

    async def get_transaction_history(self, account_id: int) -> List[Dict]:
        """获取交易历史"""
        try:
            transactions = self.transaction_repository.get_account_transactions(account_id)

            result = []
            for tx in transactions:
                # 解密交易描述（如果有）
                description = None
                if tx.description:
                    try:
                        description = self.encryption_service.decrypt_data(tx.description)
                    except:
                        description = "[Encrypted]"

                result.append({
                    "transaction_id": tx.transaction_id,
                    "from_account_id": tx.from_account_id,
                    "to_account_id": tx.to_account_id,
                    "amount": float(tx.amount),
                    "type": tx.transaction_type,
                    "status": tx.status,
                    "created_at": tx.created_at,
                    "description": description
                })

            return result
        except Exception as e:
            bank_logger.error(f"Failed to get transaction history: {str(e)}")
            raise