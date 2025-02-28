from fastapi import Depends
from sqlalchemy.orm import Session
from config.database import get_db
from services.user_service import UserService
from services.auth_service import AuthService
from services.account_service import AccountService
from services.transaction_service import TransactionService
from services.message_service import MessageService
from security.security_utils import SecurityUtils
from security.encryption import EncryptionService
from security.key_manager import KeyManager
from security.signature import SignatureService
from dal.repositories.user_repository import UserRepository
from dal.repositories.account_repository import AccountRepository
from dal.repositories.transaction_repository import TransactionRepository
from dal.repositories.encryption_keys import EncryptionKeyRepository
from dal.repositories.session_repository import SessionRepository
from dal.repositories.mfa_repository import MFARepository
from dal.repositories.message_repository import MessageRepository


def get_user_service(db: Session = Depends(get_db)):
    """获取用户服务实例"""
    user_repository = UserRepository(db)
    key_repository = EncryptionKeyRepository(db)
    key_manager = KeyManager(key_repository)
    security_utils = SecurityUtils("your-secret-key")
    encryption_service = EncryptionService(key_manager)

    return UserService(
        user_repository=user_repository,
        security_utils=security_utils,
        encryption_service=encryption_service
    )
# 获取服务实例
def get_auth_service(db: Session = Depends(get_db)):
    key_repository = EncryptionKeyRepository(db)
    user_repository = UserRepository(db)
    session_repository = SessionRepository(db)
    mfa_repository = MFARepository(db)
    key_manager = KeyManager(key_repository)
    security_utils = SecurityUtils("your-secret-key")

    return AuthService(
        user_repository=user_repository,
        session_repository=session_repository,
        mfa_repository=mfa_repository,
        security_utils=security_utils
    )


def get_account_service(db: Session = Depends(get_db)):
    account_repository = AccountRepository(db)
    key_repository = EncryptionKeyRepository(db)
    key_manager = KeyManager(key_repository)
    encryption_service = EncryptionService(key_manager)

    return AccountService(
        account_repository=account_repository,
        encryption_service=encryption_service
    )


def get_transaction_service(db: Session = Depends(get_db)):
    transaction_repository = TransactionRepository(db)
    account_repository = AccountRepository(db)
    key_repository = EncryptionKeyRepository(db)

    # 初始化密钥管理器和加密服务
    key_manager = KeyManager(key_repository)
    encryption_service = EncryptionService(key_manager)

    # 可选：初始化签名服务
    # signature_service = SignatureService(key_manager)

    return TransactionService(
        transaction_repository=transaction_repository,
        account_repository=account_repository,
        encryption_service=encryption_service
        # 如果需要签名服务，添加: signature_service=signature_service
    )


def get_message_service(db: Session = Depends(get_db)):
    """获取消息服务"""
    message_repository = MessageRepository(db)
    user_repository = UserRepository(db)
    key_repository = EncryptionKeyRepository(db)
    key_manager = KeyManager(key_repository)
    encryption_service = EncryptionService(key_manager)
    signature_service = SignatureService("your-secret-key-for-signatures")

    return MessageService(
        message_repository=message_repository,
        user_repository=user_repository,
        encryption_service=encryption_service,
        signature_service=signature_service
    )

def get_signature_service():
    """获取签名服务"""
    return SignatureService("your-secret-key-for-signatures")