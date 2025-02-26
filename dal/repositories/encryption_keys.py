from sqlalchemy.orm import Session
from ..models.encryption_keys import EncryptionKey
from .base_repository import BaseRepository
from datetime import datetime
from utils.logger import bank_logger

class EncryptionKeyRepository(BaseRepository[EncryptionKey]):
    def __init__(self, db: Session):
        super().__init__(EncryptionKey, db)

    def get_current_key(self) -> EncryptionKey:
        """获取当前活跃的密钥"""
        try:
            key = self.db.query(EncryptionKey).filter(
                EncryptionKey.status == 'active',
                EncryptionKey.expiry_date > datetime.utcnow()
            ).first()

            if key:
                bank_logger.info(f"Retrieved active key: {key.key_id}")
            else:
                bank_logger.info("No active key found")

            return key
        except Exception as e:
            bank_logger.error(f"Error retrieving current key: {str(e)}")
            raise

    def deactivate_key(self, key_id: int):
        """停用密钥"""
        key = self.get_by_id(key_id)
        if key:
            key.status = 'inactive'
            self.db.commit()