from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from .base import BaseModel

class Session(BaseModel):
    __tablename__ = 'sessions'

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    token = Column(String(256), unique=True, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(256))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Session {self.session_id} for user {self.user_id}>"