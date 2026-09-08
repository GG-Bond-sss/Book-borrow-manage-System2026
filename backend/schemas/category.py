"""分类相关 Pydantic 模型。"""
from pydantic import BaseModel
from typing import Optional


class CategoryCreateRequest(BaseModel):
    name: str


class CategoryUpdateRequest(BaseModel):
    name: str
