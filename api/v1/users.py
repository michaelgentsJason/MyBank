from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from services.user_service import UserService
from api.dependencies import get_user_service
from security.permission import has_role, get_current_user

router = APIRouter()

# 请求和响应模型
class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    status: str

class UserUpdate(BaseModel):
    email: Optional[str]
    status: Optional[str]

# API端点
@router.post("/create", response_model=UserResponse)
async def create_user(
    request: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """创建新用户"""
    try:
        user = await user_service.create_user(
            username=request.username,
            password=request.password,
            email=request.email
        )
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
@has_role(["customer", "bank_staff", "system_admin"])
async def get_user(
        user_id: int,
        user_service: UserService = Depends(get_user_service),
        current_user=Depends(get_current_user)
):
    """获取用户信息"""
    try:
        # 普通用户只能查看自己的信息
        user_roles = [role.role_name for role in current_user.roles]
        if "customer" in user_roles and user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You can only view your own information")

        user = await user_service.get_user_info(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
@has_role(["customer", "bank_staff", "system_admin"])
async def update_user(
        user_id: int,
        request: UserUpdate,
        user_service: UserService = Depends(get_user_service),
        current_user=Depends(get_current_user)
):
    """更新用户信息"""
    try:
        # 普通用户只能更新自己的信息
        user_roles = [role.role_name for role in current_user.roles]
        if "customer" in user_roles and user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You can only update your own information")

        user = await user_service.update_user(user_id, request.dict(exclude_unset=True))
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[UserResponse])
@has_role(["bank_staff", "system_admin"])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """列出所有用户"""
    try:
        users = await user_service.list_users(skip, limit)
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))