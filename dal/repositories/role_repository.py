from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from ..models.role import Role
from utils.logger import bank_logger


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        super().__init__(Role, db)

    def get_by_name(self, role_name: str) -> Role:
        """根据角色名称获取角色"""
        try:
            return self.db.query(Role).filter(Role.role_name == role_name).first()
        except Exception as e:
            bank_logger.error(f"Error getting role by name: {str(e)}")
            raise

    def get_user_roles(self, user_id: int) -> list[Role]:
        """获取用户的所有角色"""
        try:
            return (self.db.query(Role)
                    .join(Role.users)
                    .filter(Role.users.any(user_id=user_id))
                    .all())
        except Exception as e:
            bank_logger.error(f"Error getting user roles: {str(e)}")
            raise

    def create_default_roles(self):
        """创建默认角色"""
        try:
            default_roles = [
                {"role_name": "customer", "description": "Regular bank customer"},
                {"role_name": "bank_staff", "description": "Bank employee"},
                {"role_name": "system_admin", "description": "System administrator"}
            ]

            for role_data in default_roles:
                if not self.get_by_name(role_data["role_name"]):
                    self.create(role_data)

            self.db.commit()
        except Exception as e:
            bank_logger.error(f"Error creating default roles: {str(e)}")
            self.db.rollback()
            raise