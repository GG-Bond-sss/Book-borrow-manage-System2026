"""AI 助手路由。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models.user import User
from response import success
from schemas.ai import ChatRequest
from services.ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["AI 助手"])


@router.post("/chat")
async def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """AI 助手对话。"""
    service = AIService()
    history = [h.model_dump() for h in req.history] if req.history else None
    reply = await service.chat(req.message, history)
    return success(data={"reply": reply})
