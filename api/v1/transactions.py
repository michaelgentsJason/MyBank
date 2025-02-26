from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from services.transaction_service import TransactionService
from api.dependencies import get_transaction_service
from security.permission import has_role, owns_account, get_current_user

router = APIRouter()

# 请求和响应模型
class TransactionCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    transaction_id: int
    from_account_id: int
    to_account_id: int
    amount: Decimal
    type: str
    status: str
    created_at: datetime
    description: Optional[str] = None

# API端点
@router.post("/create", response_model=TransactionResponse)
@owns_account
async def create_transaction(
    request: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user = Depends(get_current_user)
):
    """创建新交易"""
    try:
        transaction = await transaction_service.create_transaction(
            from_account_id=request.from_account_id,
            to_account_id=request.to_account_id,
            amount=request.amount,
            description=request.description
        )
        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{transaction_id}", response_model=TransactionResponse)
@has_role(["customer", "bank_staff", "system_admin"])
async def get_transaction(
        transaction_id: int,
        transaction_service: TransactionService = Depends(get_transaction_service),
        current_user=Depends(get_current_user)
):
    """获取交易详情"""
    try:
        transaction = await transaction_service.get_transaction(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # 普通用户只能查看与自己账户相关的交易
        user_roles = [role.role_name for role in current_user.roles]
        if "customer" in user_roles:
            # 获取用户的账户列表
            from services.account_service import AccountService
            from api.dependencies import get_account_service
            account_service = get_account_service()
            user_accounts = await account_service.get_user_accounts(current_user.user_id)
            user_account_ids = [acc["account_id"] for acc in user_accounts]

            # 检查交易是否属于用户
            if (transaction["from_account_id"] not in user_account_ids and
                    transaction["to_account_id"] not in user_account_ids):
                raise HTTPException(status_code=403, detail="Not authorized to view this transaction")

        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/account/{account_id}", response_model=List[TransactionResponse])
@owns_account
async def get_account_transactions(
    account_id: int,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user = Depends(get_current_user)
):
    """获取账户的交易历史"""
    try:
        transactions = await transaction_service.get_transaction_history(account_id)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))