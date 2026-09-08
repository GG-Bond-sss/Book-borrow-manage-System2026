"""收藏相关 Pydantic 模型。"""
from pydantic import BaseModel
from typing import Optional


class FavoriteToggleRequest(BaseModel):
    book_id: int


class FavoriteListQuery(BaseModel):
    page: int = 1
    page_size: int = 10
