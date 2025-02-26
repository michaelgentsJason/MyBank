from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.auth_service import AuthService
from api.dependencies import get_auth_service
from typing import Optional
from security.permission import has_role, get_current_user

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str
    mfa_code: Optional[str] = None

class LoginResponse(BaseModel):
    user_id: int
    requires_mfa: bool = False
    token: Optional[str] = None  # 可选，在MFA情况下没有
    temp_token: Optional[str] = None  # 可选，仅在MFA情况下有

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        result = await auth_service.login(
            username=request.username,
            password=request.password
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-mfa")
async def verify_mfa(
    temp_token: str,
    mfa_code: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """验证MFA码"""
    result = await auth_service.verify_mfa(temp_token, mfa_code)
    return result


@router.post("/setup-mfa")
@has_role(["customer", "bank_staff", "system_admin"])
async def setup_mfa(
        user_id: int,
        auth_service: AuthService = Depends(get_auth_service),
        current_user=Depends(get_current_user)
):
    """设置MFA"""
    try:
        # 普通用户只能为自己设置MFA
        user_roles = [role.role_name for role in current_user.roles]
        if "customer" in user_roles and user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You can only setup MFA for yourself")

        result = await auth_service.setup_mfa(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))