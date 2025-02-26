from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from services.account_service import AccountService
from api.dependencies import get_account_service, get_db
from security.permission import has_role, owns_account, get_current_user
from sqlalchemy.orm import Session


router = APIRouter()

# 请求和响应模型
class AccountCreate(BaseModel):
    user_id: int
    account_type: str

class AccountResponse(BaseModel):
    account_id: int
    account_number: str
    account_type: str
    balance: Decimal
    status: str

class AccountUpdate(BaseModel):
    status: Optional[str]

# 添加存款请求模型
class DepositRequest(BaseModel):
    amount: Decimal

@router.post("/{account_id}/deposit", response_model=AccountResponse)
@owns_account
async def deposit(
    account_id: int,
    request: DepositRequest,
    account_service: AccountService = Depends(get_account_service),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """向账户存款"""
    try:
        result = await account_service.deposit(account_id, request.amount)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API端点
@router.post("/create", response_model=AccountResponse)
@has_role(["customer", "bank_stuff", "system_admin"])
async def create_account(
    request: AccountCreate,
    account_service: AccountService = Depends(get_account_service),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建新账户"""
    try:
        # 如果是普通用户，只能为自己创建账户
        if "customer" in [r.role_name for r in current_user.roles]:
            if request.user_id != current_user.user_id:
                raise HTTPException(status_code=403, detail="You can only create accounts for yourself")

        account = await account_service.create_account(
            user_id=request.user_id,
            account_type=request.account_type
        )
        return account
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

router.get("/{account_id}", response_model=AccountResponse)
@owns_account
async def get_account(
    account_id: int,
    account_service: AccountService = Depends(get_account_service),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取账户信息"""
    try:
        account = await account_service.get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=List[AccountResponse])
@has_role(["customer", "bank_staff", "system_admin"])
async def get_user_accounts(
        user_id: int,
        account_service: AccountService = Depends(get_account_service),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """获取用户的所有账户"""
    try:
        # 普通用户只能查看自己的账户
        if "customer" in [r.role_name for r in current_user.roles] and user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You can only view your own accounts")

        accounts = await account_service.get_user_accounts(user_id)
        return accounts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{account_id}/balance")
async def get_account_balance(
    account_id: int,
    account_service: AccountService = Depends(get_account_service)
):
    """获取账户余额"""
    try:
        balance = await account_service.get_account_balance(account_id)
        return {"balance": balance}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))