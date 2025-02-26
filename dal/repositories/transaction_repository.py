from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from ..models.transaction import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(Transaction, db)

    def get_account_transactions(self, account_id: int) -> list[Transaction]:
        return self.db.query(Transaction).filter(
            (Transaction.from_account_id == account_id) |
            (Transaction.to_account_id == account_id)
        ).all()

    def get_pending_transactions(self) -> list[Transaction]:
        return self.db.query(Transaction).filter(
            Transaction.status == 'pending'
        ).all()