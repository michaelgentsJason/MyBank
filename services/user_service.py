from typing import Optional, Dict, List
from datetime import datetime
from dal.repositories.user_repository import UserRepository
from dal.repositories.role_repository import RoleRepository
from security.security_utils import SecurityUtils
from security.encryption import EncryptionService
from utils.exceptions import ValidationError, AuthenticationError
from utils.logger import bank_logger
from sqlalchemy import text



class UserService:
    def __init__(
            self,
            user_repository: UserRepository,
            security_utils: SecurityUtils,
            encryption_service: EncryptionService
    ):
        self.user_repository = user_repository
        self.security_utils = security_utils
        self.encryption_service = encryption_service

    async def create_user(self, username: str, password: str, email: str) -> Dict:
        """
        创建新用户（默认为客户角色）
        :param username: 用户名
        :param password: 密码
        :param email: 电子邮件
        :return: 用户信息字典
        """
        try:
            # 检查用户名是否已存在
            if self.user_repository.get_by_username(username):
                raise ValidationError("Username already exists")

            # 检查邮箱是否已存在
            if self.user_repository.get_by_email(email):
                raise ValidationError("Email already exists")

            # 密码哈希
            password_hash = self.security_utils.hash_password(password)
            # 加密邮箱
            encrypted_email = self.encryption_service.encrypt_data(email)

            # 创建用户
            user_data = {
                "username": username,
                "password_hash": password_hash,
                "email": encrypted_email,
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            user = self.user_repository.create(user_data)

            # 获取customer角色ID并分配给新用户
            role_repository = RoleRepository(self.user_repository.db)
            customer_role = role_repository.get_by_name("customer")
            if customer_role:
                # 使用SQLAlchemy的方式插入用户角色关联
                sql = text("""
                            INSERT INTO user_roles (user_id, role_id)
                            VALUES (:user_id, :role_id)
                        """)
                self.user_repository.db.execute(sql, {
                    "user_id": user.user_id,
                    "role_id": customer_role.role_id
                })
                self.user_repository.db.commit()
                bank_logger.info(f"Assigned customer role to user: {username}")
            else:
                bank_logger.warning(f"Customer role not found when creating user: {username}")

            return {
                "user_id": user.user_id,
                "username": user.username,
                "email": email,  # 返回解密后的邮箱
                "status": user.status,
                "created_at": user.created_at
            }
        except Exception as e:
            bank_logger.error(f"Failed to create user: {str(e)}")
            raise

    async def get_user_info(self, user_id: int) -> Optional[Dict]:
        """
        获取用户信息
        :param user_id: 用户ID
        :return: 用户信息字典或None
        """
        try:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return None

            # 解密邮箱
            decrypted_email = self.encryption_service.decrypt_data(user.email)

            return {
                "user_id": user.user_id,
                "username": user.username,
                "email": decrypted_email,
                "status": user.status,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        except Exception as e:
            bank_logger.error(f"Failed to get user info: {str(e)}")
            raise

    async def update_user(self, user_id: int, update_data: Dict) -> Optional[Dict]:
        """
        更新用户信息
        :param user_id: 用户ID
        :param update_data: 要更新的数据字典
        :return: 更新后的用户信息
        """
        try:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise ValidationError("User not found")

            # 如果更新邮箱，需要加密
            if 'email' in update_data:
                if self.user_repository.get_by_email(update_data['email']):
                    raise ValidationError("Email already exists")
                update_data['email'] = self.encryption_service.encrypt_data(update_data['email'])

            # 如果更新密码，需要哈希
            if 'password' in update_data:
                update_data['password_hash'] = self.security_utils.hash_password(update_data.pop('password'))

            # 更新时间戳
            update_data['updated_at'] = datetime.utcnow()

            # 更新用户信息
            updated_user = self.user_repository.update(user_id, update_data)
            if not updated_user:
                return None

            # 解密邮箱用于返回
            decrypted_email = self.encryption_service.decrypt_data(updated_user.email)

            return {
                "user_id": updated_user.user_id,
                "username": updated_user.username,
                "email": decrypted_email,
                "status": updated_user.status,
                "updated_at": updated_user.updated_at
            }
        except Exception as e:
            bank_logger.error(f"Failed to update user: {str(e)}")
            raise

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        修改用户密码
        :param user_id: 用户ID
        :param old_password: 旧密码
        :param new_password: 新密码
        :return: 是否成功
        """
        try:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise ValidationError("User not found")

            # 验证旧密码
            if not self.security_utils.verify_password(old_password, user.password_hash):
                raise AuthenticationError("Invalid old password")

            # 生成新密码哈希
            new_password_hash = self.security_utils.hash_password(new_password)

            # 更新密码
            success = self.user_repository.update(user_id, {
                "password_hash": new_password_hash,
                "updated_at": datetime.utcnow()
            })

            return bool(success)
        except Exception as e:
            bank_logger.error(f"Failed to change password: {str(e)}")
            raise

    async def deactivate_user(self, user_id: int) -> bool:
        """
        停用用户账户
        :param user_id: 用户ID
        :return: 是否成功
        """
        try:
            success = self.user_repository.update(user_id, {
                "status": "suspended",
                "updated_at": datetime.utcnow()
            })
            return bool(success)
        except Exception as e:
            bank_logger.error(f"Failed to deactivate user: {str(e)}")
            raise

    async def activate_user(self, user_id: int) -> bool:
        """
        激活用户账户
        :param user_id: 用户ID
        :return: 是否成功
        """
        try:
            success = self.user_repository.update(user_id, {
                "status": "active",
                "updated_at": datetime.utcnow()
            })
            return bool(success)
        except Exception as e:
            bank_logger.error(f"Failed to activate user: {str(e)}")
            raise

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        获取用户列表
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :return: 用户列表
        """
        try:
            users = self.user_repository.get_all(skip=skip, limit=limit)
            return [{
                "user_id": user.user_id,
                "username": user.username,
                "email": self.encryption_service.decrypt_data(user.email),
                "status": user.status,
                "created_at": user.created_at
            } for user in users]
        except Exception as e:
            bank_logger.error(f"Failed to list users: {str(e)}")
            raise