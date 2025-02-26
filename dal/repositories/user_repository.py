from sqlalchemy.orm import Session
from dal.repositories.base_repository import BaseRepository
from dal.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()
