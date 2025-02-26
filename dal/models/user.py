from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
from .user_role import UserRole
from .role import Role
from .session import Session
from .audit_log import AuditLog

class User(BaseModel):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    status = Column(Enum('active', 'locked', 'suspended'), nullable=False, default='active')

    # Add relationships
    accounts = relationship("Account", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    sessions = relationship("Session", backref="user")
    audit_logs = relationship("AuditLog", backref="user")

    def __repr__(self):
        return f"<User {self.username}>"