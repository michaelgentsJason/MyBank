from fastapi import APIRouter, Depends, HTTPException
from security.blockchain import blockchain_instance
from security.permission import has_role, get_current_user

router = APIRouter()

@router.get("/blocks")
@has_role(["customer", "bank_staff", "system_admin"])
async def get_blocks(current_user = Depends(get_current_user)):
    """获取所有区块"""
    return blockchain_instance.get_blocks()

@router.get("/validate")
@has_role(["bank_staff", "system_admin"])
async def validate_chain(current_user = Depends(get_current_user)):
    """验证整个区块链的完整性"""
    return {"is_valid": blockchain_instance.is_chain_valid()}

@router.get("/transaction/{transaction_id}")
@has_role(["customer", "bank_staff", "system_admin"])
async def verify_transaction(
    transaction_id: int,
    current_user = Depends(get_current_user)
):
    """验证交易是否在区块链中且未被篡改"""
    result = blockchain_instance.verify_transaction(transaction_id)
    if not result["transaction_found"]:
        raise HTTPException(status_code=404, detail="Transaction not found in blockchain")
    return result