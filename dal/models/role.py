from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel
from .user_role import UserRole

class Role(BaseModel):
    __tablename__ = 'roles'

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 与User的关系
    users = relationship('User', secondary=UserRole.__table__, back_populates='roles')

    def __repr__(self):
        return f"<Role {self.role_name}>"