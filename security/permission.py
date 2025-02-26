from functools import wraps
from fastapi import Depends, HTTPException, status
from dal.repositories.user_repository import UserRepository
from dal.repositories.role_repository import RoleRepository
from security.security_utils import SecurityUtils
from api.dependencies import get_db
from sqlalchemy.orm import Session


def get_token_from_header(authorization: str = None):
    """从认证头中提取令牌"""
    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


def get_current_user(db: Session = Depends(get_db), authorization: str = None):
    """获取当前登录用户"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = get_token_from_header(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    security_utils = SecurityUtils("your-secret-key")

    try:
        # 解析令牌
        payload = security_utils.verify_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 获取用户
    user_repository = UserRepository(db)
    user = user_repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def has_role(required_roles):
    """检查用户是否拥有指定角色"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取当前用户和数据库会话
            db = kwargs.get("db") or next(get_db())
            user = kwargs.get("current_user")
            if not user:
                authorization = kwargs.get("authorization")
                user = get_current_user(db, authorization)

            # 获取用户角色
            role_repository = RoleRepository(db)
            user_roles = role_repository.get_user_roles(user.user_id)
            user_role_names = [role.role_name for role in user_roles]

            # 检查是否拥有所需角色
            if not any(role in user_role_names for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied. Required roles: " + ", ".join(required_roles)
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def is_account_owner(account_id: int, user_id: int, db: Session):
    """检查用户是否是账户的所有者"""
    from dal.repositories.account_repository import AccountRepository
    account_repository = AccountRepository(db)
    account = account_repository.get_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    if account.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account"
        )

    return True


def owns_account(func):
    """检查用户是否拥有指定账户"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 获取当前用户和数据库会话
        db = kwargs.get("db") or next(get_db())
        user = kwargs.get("current_user")
        if not user:
            authorization = kwargs.get("authorization")
            user = get_current_user(db, authorization)

        # 获取账户ID
        account_id = kwargs.get("account_id")
        if not account_id:
            # 尝试从请求体中获取
            request = kwargs.get("request")
            if request and hasattr(request, "from_account_id"):
                account_id = request.from_account_id

        # 如果是管理员或银行员工，直接放行
        role_repository = RoleRepository(db)
        user_roles = role_repository.get_user_roles(user.user_id)
        user_role_names = [role.role_name for role in user_roles]

        if "system_admin" in user_role_names or "bank_staff" in user_role_names:
            return await func(*args, **kwargs)

        # 检查普通用户是否是账户所有者
        is_account_owner(account_id, user.user_id, db)

        return await func(*args, **kwargs)

    return wrapper