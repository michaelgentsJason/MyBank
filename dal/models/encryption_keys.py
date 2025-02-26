from sqlalchemy import Column, Integer, String, Enum, DateTime, Text
from datetime import datetime
from .base import BaseModel


class EncryptionKey(BaseModel):
    __tablename__ = 'encryption_keys'

    key_id = Column(Integer, primary_key=True, autoincrement=True)
    key_type = Column(Enum('symmetric', 'asymmetric'), nullable=False)
    key_value = Column(Text, nullable=False)  # 确保使用key_value作为属性名
    status = Column(Enum('active', 'inactive', 'revoked'), nullable=False, default='active')
    expiry_date = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<EncryptionKey {self.key_id}: {self.key_type}>"