from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from ..models.mfa_config import MFAConfig
from utils.logger import bank_logger
from typing import Optional


# class MFARepository(BaseRepository[MFAConfig]):
#     def __init__(self, db: Session):
#         super().__init__(MFAConfig, db)
#
#     def get_user_config(self, user_id: int) -> Optional[MFAConfig]:
#         """获取用户的MFA配置"""
#         try:
#             return self.db.query(MFAConfig).filter(
#                 MFAConfig.user_id == user_id,
#                 MFAConfig.is_enabled == True  # 只返回已启用的MFA配置
#             ).first()
#         except Exception as e:
#             bank_logger.error(f"Error getting MFA config: {str(e)}")
#             return None
#
#     def save_verification_code(self, user_id: int, code: str) -> MFAConfig:
#         """保存验证码"""
#         config = self.get_user_config(user_id)
#         if not config:
#             config = MFAConfig(user_id=user_id)
#             self.db.add(config)
#
#         config.verification_code = code
#         config.code_expires_at = datetime.utcnow() + timedelta(minutes=5)
#         config.is_enabled = True
#
#         self.db.commit()
#         return config
#
#     def verify_code(self, user_id: int, code: str) -> bool:
#         """验证代码"""
#         config = self.get_user_config(user_id)
#         if not config:
#             return False
#
#         if not config.is_enabled:
#             return False
#
#         if datetime.utcnow() > config.code_expires_at:
#             return False
#
#         return config.verification_code == code

class MFARepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_config(self, user_id: int) -> MFAConfig:
        """获取用户的MFA配置"""
        return self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user_id
        ).first()

    def save_verification_code(self, user_id: int, code: str, expires_in: int = 300) -> MFAConfig:
        """保存新的验证码"""
        config = self.get_user_config(user_id)
        if not config:
            config = MFAConfig(user_id=user_id)
            self.db.add(config)

        config.verification_code = code
        config.code_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        try:
            self.db.commit()
            return config
        except Exception as e:
            self.db.rollback()
            bank_logger.error(f"Failed to save verification code: {str(e)}")
            raise

    def verify_code(self, user_id: int, code: str) -> bool:
        """验证MFA代码"""
        config = self.get_user_config(user_id)
        if not config:
            return False

        if datetime.utcnow() > config.code_expires_at:
            return False

        return config.verification_code == code