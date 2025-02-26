from sqlalchemy import Column, Integer, String, Enum, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Transaction(BaseModel):
    __tablename__ = 'transactions'

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    from_account_id = Column(Integer, ForeignKey('accounts.account_id'))
    to_account_id = Column(Integer, ForeignKey('accounts.account_id'))
    amount = Column(DECIMAL(20, 2), nullable=False)
    transaction_type = Column(Enum('deposit', 'withdrawal', 'transfer', 'payment'), nullable=False)
    status = Column(Enum('pending', 'completed', 'failed', 'cancelled'), nullable=False)
    signature = Column(String(256))
    description = Column(String(256))

    # 关系定义
    from_account = relationship("Account", foreign_keys=[from_account_id])
    to_account = relationship("Account", foreign_keys=[to_account_id])

    def __repr__(self):
        return f"<Transaction {self.transaction_id}>"