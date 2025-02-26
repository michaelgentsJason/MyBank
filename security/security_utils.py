import bcrypt
import secrets
from datetime import datetime, timedelta
import jwt
from utils.logger import bank_logger
from utils.exceptions import SecurityError

class SecurityUtils:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    @staticmethod
    def hash_password(password: str) -> str:
        """对密码进行哈希"""
        try:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode(), salt).decode()
        except Exception as e:
            bank_logger.error(f"Password hashing failed: {str(e)}")
            raise SecurityError("Failed to hash password")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception as e:
            bank_logger.error(f"Password verification failed: {str(e)}")
            return False

    def generate_token(self, user_id: int, token_type: str = 'full') -> str:
        """
        生成JWT令牌
        :param user_id: 用户ID
        :param token_type: token类型 ('temp', 'initial', 'full')
        :return: JWT token
        """
        try:
            # 根据token类型设置过期时间
            if token_type == 'full':
                expiry = datetime.utcnow() + timedelta(hours=24)
            elif token_type == 'temp':
                expiry = datetime.utcnow() + timedelta(minutes=5)
            else:  # initial token
                expiry = datetime.utcnow() + timedelta(hours=1)

            payload = {
                'user_id': user_id,
                'exp': expiry,
                'iat': datetime.utcnow(),
                'token_type': token_type
            }
            return jwt.encode(payload, self.secret_key, algorithm='HS256')
        except Exception as e:
            bank_logger.error(f"Token generation failed: {str(e)}")
            raise SecurityError("Failed to generate token")


    # def generate_temp_token(self, user_id: int) -> str:
    #     """生成临时令牌（用于MFA验证）"""
    #     try:
    #         payload = {
    #             'user_id': user_id,
    #             'exp': datetime.utcnow() + timedelta(minutes=5),
    #             'type': 'temp'
    #         }
    #         return jwt.encode(payload, self.secret_key, algorithm='HS256')
    #     except Exception as e:
    #         bank_logger.error(f"Temp token generation failed: {str(e)}")
    #         raise SecurityError("Failed to generate temporary token")

    def verify_token(self, token: str, expected_type: str = None) -> dict:
        """
        验证JWT令牌
        :param token: JWT token
        :param expected_type: 期望的token类型
        :return: token payload
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])

            # 如果指定了expected_type，验证token类型
            if expected_type and payload.get('token_type') != expected_type:
                raise SecurityError(f"Invalid token type. Expected {expected_type}")

            return payload
        except jwt.ExpiredSignatureError:
            raise SecurityError("Token has expired")
        except jwt.InvalidTokenError:
            raise SecurityError("Invalid token")

    # def verify_temp_token(self, token: str) -> dict:
    #     """验证临时令牌"""
    #     try:
    #         payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
    #         if payload.get('type') != 'temp':
    #             raise SecurityError("Invalid token type")
    #         return payload
    #     except jwt.ExpiredSignatureError:
    #         raise SecurityError("Temporary token has expired")
    #     except jwt.InvalidTokenError:
    #         raise SecurityError("Invalid temporary token")

    # 为了保持向后兼容，保留这些方法但使用统一的实现
    def generate_temp_token(self, user_id: int) -> str:
        """生成临时令牌（用于MFA验证）"""
        return self.generate_token(user_id, token_type='temp')

    def verify_temp_token(self, token: str) -> dict:
        """验证临时令牌"""
        return self.verify_token(token, expected_type='temp')