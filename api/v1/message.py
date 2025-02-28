from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from services.message_service import MessageService
from api.dependencies import get_message_service
from security.permission import has_role, get_current_user

router = APIRouter()

# 请求模型
class MessageCreate(BaseModel):
    recipient_id: int
    subject: str
    content: str

# 响应模型
class MessageResponse(BaseModel):
    message_id: int
    sender_id: int
    sender_name: str
    recipient_id: int
    recipient_name: str
    subject: str
    created_at: datetime
    status: str
    read_at: Optional[datetime] = None

class MessageDetailResponse(MessageResponse):
    content: str
    signature_valid: bool

# API端点
@router.post("/send", response_model=MessageResponse)
@has_role(["customer", "bank_staff", "system_admin"])
async def send_message(
    request: MessageCreate,
    message_service: MessageService = Depends(get_message_service),
    current_user = Depends(get_current_user)
):
    """发送加密消息"""
    try:
        result = await message_service.send_message(
            sender_id=current_user.user_id,
            recipient_id=request.recipient_id,
            subject=request.subject,
            content=request.content
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/inbox", response_model=List[MessageResponse])
@has_role(["customer", "bank_staff", "system_admin"])
async def get_inbox(
    message_service: MessageService = Depends(get_message_service),
    current_user = Depends(get_current_user)
):
    """获取收件箱消息"""
    try:
        messages = await message_service.get_messages(current_user.user_id)
        return messages
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sent", response_model=List[MessageResponse])
@has_role(["customer", "bank_staff", "system_admin"])
async def get_sent_messages(
    message_service: MessageService = Depends(get_message_service),
    current_user = Depends(get_current_user)
):
    """获取已发送消息"""
    try:
        messages = await message_service.get_messages(current_user.user_id, sent=True)
        return messages
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{message_id}", response_model=MessageDetailResponse)
@has_role(["customer", "bank_staff", "system_admin"])
async def read_message(
    message_id: int,
    message_service: MessageService = Depends(get_message_service),
    current_user = Depends(get_current_user)
):
    """读取消息内容"""
    try:
        message = await message_service.read_message(message_id, current_user.user_id)
        return message
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))