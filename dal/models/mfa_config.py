from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime
from .base import BaseModel

class MFAConfig(BaseModel):
    __tablename__ = 'mfa_configs'

    config_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)
    verification_code = Column(String(6))
    code_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<MFAConfig user_id={self.user_id}>"