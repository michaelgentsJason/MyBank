from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from ..models.user_role import UserRole
from utils.logger import bank_logger

class UserRoleRepository(BaseRepository[UserRole]):
    def __init__(self, db: Session):
        super().__init__(UserRole, db)

    def assign_role(self, user_id: int, role_id: int) -> UserRole:
        """为用户分配角色"""
        try:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(user_role)
            self.db.commit()
            return user_role
        except Exception as e:
            bank_logger.error(f"Error assigning role: {str(e)}")
            self.db.rollback()
            raise

    def remove_role(self, user_id: int, role_id: int) -> bool:
        """移除用户的角色"""
        try:
            result = self.db.query(UserRole).filter(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            ).delete()
            self.db.commit()
            return result > 0
        except Exception as e:
            bank_logger.error(f"Error removing role: {str(e)}")
            self.db.rollback()
            raise

    def get_user_role_ids(self, user_id: int) -> list[int]:
        """获取用户的所有角色ID"""
        try:
            roles = self.db.query(UserRole.role_id).filter(
                UserRole.user_id == user_id
            ).all()
            return [role[0] for role in roles]
        except Exception as e:
            bank_logger.error(f"Error getting user role IDs: {str(e)}")
            raise