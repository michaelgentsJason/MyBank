from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from ..models.account import Account


class AccountRepository(BaseRepository[Account]):
    def __init__(self, db: Session):
        super().__init__(Account, db)

    def get_by_account_number(self, account_number: str) -> Account:
        return self.db.query(Account).filter(Account.account_number == account_number).first()

    def get_user_accounts(self, user_id: int) -> list[Account]:
        return self.db.query(Account).filter(Account.user_id == user_id).all()

    def update_balance(self, account_id: int, amount: float) -> Account:
        account = self.get_by_id(account_id)
        if account:
            account.balance += amount
            self.db.commit()
            self.db.refresh(account)
        return account