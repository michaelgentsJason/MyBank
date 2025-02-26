from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime
from .base import BaseModel

class UserRole(BaseModel):
    __tablename__ = 'user_roles'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.role_id'), primary_key=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"