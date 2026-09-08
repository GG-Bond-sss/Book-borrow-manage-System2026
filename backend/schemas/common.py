"""通用 Pydantic 模型：分页等。"""
from typing import Any, List, Optional
from pydantic import BaseModel


class PageResponse(BaseModel):
    """分页响应模型。"""
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0
    items: List[Any] = []


class ApiResponse(BaseModel):
    """统一响应模型。"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
