"""AI 助手相关 Pydantic 模型。"""
from pydantic import BaseModel
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str  # user / assistant
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    reply: str
