import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
from dal.repositories.user_repository import UserRepository
from dal.repositories.session_repository import SessionRepository
from dal.repositories.mfa_repository import MFARepository
from security.security_utils import SecurityUtils
from utils.exceptions import AuthenticationError, ValidationError
from utils.logger import bank_logger


class AuthService:
    def __init__(
            self,
            user_repository: UserRepository,
            session_repository: SessionRepository,
            mfa_repository: MFARepository,
            security_utils: SecurityUtils
    ):
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.mfa_repository = mfa_repository
        self.security_utils = security_utils

    async def register(self, username: str, password: str, email: str) -> Dict:
        """
        用户注册
        :param username: 用户名
        :param password: 密码
        :param email: 电子邮件
        :return: 用户信息和令牌
        """
        try:
            # 检查用户名是否已存在
            if self.user_repository.get_by_username(username):
                raise ValidationError("Username already exists")

            # 检查邮箱是否已存在
            if self.user_repository.get_by_email(email):
                raise ValidationError("Email already exists")

            # 创建用户
            password_hash = self.security_utils.hash_password(password)
            user_data = {
                "username": username,
                "password_hash": password_hash,
                "email": email,
                "status": "active"
            }
            user = self.user_repository.create(user_data)

            # 创建会话并返回令牌
            return await self.create_session(user.user_id)

        except Exception as e:
            bank_logger.error(f"Registration failed: {str(e)}")
            raise

    async def login(self, username: str, password: str, ip_address: str = None) -> Dict:
        """
        用户登录：必须采用MFA
        :param username: 用户名
        :param password: 密码
        :param ip_address: IP地址
        :return: 登录结果和令牌
        """
        try:
            # 验证用户名和密码
            user = self.user_repository.get_by_username(username)
            if not user:
                raise AuthenticationError("Invalid username or password")

            if not self.security_utils.verify_password(password, user.password_hash):
                raise AuthenticationError("Invalid username or password")

            # 检查用户状态
            if user.status != "active":
                raise AuthenticationError("Account is not active")

            # # 检查是否启用了MFA
            # mfa_config = self.mfa_repository.get_user_config(user.user_id)
            # if mfa_config and mfa_config.is_enabled:

            # 返回临时token用于MFA验证
            return {
                "user_id": user.user_id,
                "requires_mfa": True,
                "temp_token": self.security_utils.generate_token(user.user_id, token_type='temp'),
                "initial_access_token": None,
                "full_access_token": None
            }

            # # 未启用MFA，直接创建完整访问token
            # session_data = await self.create_session(user.user_id, ip_address, token_type='full')
            #
            # # 确保返回格式一致
            # return {
            #     "user_id": user.user_id,
            #     "requires_mfa": False,
            #     "temp_token": None,
            #     "initial_access_token": None,
            #     "full_access_token": session_data["token"]
            # }

        except Exception as e:
            bank_logger.error(f"Login failed: {str(e)}")
            raise

    async def verify_mfa(self, temp_token: str, mfa_code: str, ip_address: str = None) -> Dict:
        """
        验证MFA码
        :param temp_token: 临时token
        :param mfa_code: MFA验证码
        :param ip_address: IP地址
        :return: 验证结果和完整访问token
        """
        try:
            # 验证临时token
            token_data = self.security_utils.verify_token(temp_token, expected_type='temp')
            user_id = token_data.get("user_id")

            # 验证MFA代码
            if not self.mfa_repository.verify_code(user_id, mfa_code):
                raise AuthenticationError("Invalid MFA code")

            # 验证成功，创建完整访问token
            session_data = await self.create_session(user_id, ip_address, token_type='full')

            return {
                "user_id": user_id,
                "requires_mfa": False,
                "temp_token": None,
                "initial_access_token": None,
                "full_access_token": session_data["token"]
            }

        except Exception as e:
            bank_logger.error(f"MFA verification failed: {str(e)}")
            raise

    async def setup_mfa(self, user_id: int) -> Dict:
        """
        设置MFA
        :param user_id: 用户ID
        :return: MFA设置结果
        """
        try:
            # 生成验证码
            verification_code = self.generate_verification_code()

            # 保存MFA配置
            self.mfa_repository.save_verification_code(
                user_id=user_id,
                code=verification_code
            )

            # 模拟发送验证码
            bank_logger.info(f"Verification code for user {user_id}: {verification_code}")

            return {
                "message": "Verification code has been sent",
                "mfa_code": verification_code,  # 在实际生产环境中应通过安全渠道发送
                "expires_in": 300  # 5分钟过期
            }

        except Exception as e:
            bank_logger.error(f"MFA setup failed: {str(e)}")
            raise

    async def logout(self, token: str) -> bool:
        """
        用户登出
        :param token: 会话令牌
        :return: 是否成功登出
        """
        try:
            # 使会话失效
            return self.session_repository.invalidate_session_by_token(token)
        except Exception as e:
            bank_logger.error(f"Logout failed: {str(e)}")
            raise

    async def create_session(self, user_id: int, ip_address: str = None, token_type: str = 'full') -> Dict:
        """
        创建新的会话
        :param user_id: 用户ID
        :param ip_address: IP地址
        :param token_type: token类型('temp', 'initial', 'full')
        :return: 会话信息
        """
        try:
            # 根据类型生成对应token
            token = self.security_utils.generate_token(user_id, token_type)

            # 设置过期时间（full token 24小时，其他1小时）
            expires_at = datetime.utcnow() + timedelta(
                hours=24 if token_type == 'full' else 1
            )

            # 创建会话记录
            self.session_repository.create_session(
                user_id=user_id,
                token=token,
                expires_at=expires_at,
                ip_address=ip_address
            )

            return {
                "user_id": user_id,
                "token": token,
                "token_type": token_type,
                "expires_at": expires_at
            }

        except Exception as e:
            bank_logger.error(f"Session creation failed: {str(e)}")
            raise

    def generate_verification_code(self, length: int = 6) -> str:
        """
        生成验证码
        :param length: 验证码长度
        :return: 验证码
        """
        return ''.join(random.choices(string.digits, k=length))

    async def verify_token(self, token: str) -> Optional[Dict]:
        """
        验证令牌
        :param token: 会话令牌
        :return: 令牌信息
        """
        try:
            # 验证令牌有效性
            token_data = self.security_utils.verify_token(token)
            if not token_data:
                return None

            # 检查会话是否有效
            session = self.session_repository.get_active_session(token)
            if not session:
                return None

            return token_data

        except Exception as e:
            bank_logger.error(f"Token verification failed: {str(e)}")
            return None

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        修改密码
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

            # 更新密码
            new_password_hash = self.security_utils.hash_password(new_password)
            success = self.user_repository.update(user_id, {
                "password_hash": new_password_hash,
                "updated_at": datetime.utcnow()
            })

            if success:
                # 使所有现有会话失效
                self.session_repository.invalidate_all_user_sessions(user_id)

            return bool(success)

        except Exception as e:
            bank_logger.error(f"Password change failed: {str(e)}")
            raise