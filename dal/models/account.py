from sqlalchemy import Column, Integer, String, Enum, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Account(BaseModel):
    __tablename__ = 'accounts'

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    account_type = Column(Enum('savings', 'checking', 'investment', 'loan'), nullable=False)
    account_number = Column(String(20), unique=True, nullable=False)
    balance = Column(DECIMAL(20, 2), nullable=False, default=0.00)
    status = Column(Enum('active', 'frozen', 'closed'), nullable=False, default='active')

    # 关系定义
    user = relationship("User", back_populates="accounts")

    def __repr__(self):
        return f"<Account {self.account_number}>"