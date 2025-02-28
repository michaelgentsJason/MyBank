from config.database import engine
from dal.models.base import Base
# 导入所有模型
from config.database import engine, Base
from dal.models.user import User
from dal.models.account import Account
from dal.models.transaction import Transaction
from dal.models.encryption_keys import EncryptionKey
from dal.models.role import Role
from dal.models.user_role import UserRole
from dal.models.audit_log import AuditLog
from dal.models.session import Session
from dal.models.mfa_config import MFAConfig
from dal.models.message import SecureMessage

def init_db():
    # 删除所有现有表
    Base.metadata.drop_all(bind=engine)
    # 创建所有表
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("数据库表创建成功！")
