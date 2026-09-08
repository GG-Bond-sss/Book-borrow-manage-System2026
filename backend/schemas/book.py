"""图书相关 Pydantic 模型。"""
from pydantic import BaseModel, field_validator
from typing import Optional


class BookCreateRequest(BaseModel):
    title: str
    author: str
    isbn: str
    category_id: int
    publisher: Optional[str] = None
    publish_year: Optional[int] = None
    total_count: int = 1
    summary: Optional[str] = None
    cover_url: Optional[str] = None

    @field_validator("title", "author", "isbn", "category_id")
    @classmethod
    def not_empty(cls, v):
        if not v:
            raise ValueError("该字段不能为空")
        return v

    @field_validator("total_count")
    @classmethod
    def validate_total(cls, v):
        if v < 1:
            raise ValueError("总馆藏数量必须大于等于1")
        return v


class BookUpdateRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    category_id: Optional[int] = None
    publisher: Optional[str] = None
    publish_year: Optional[int] = None
    total_count: Optional[int] = None
    summary: Optional[str] = None
    cover_url: Optional[str] = None

    @field_validator("total_count")
    @classmethod
    def validate_total(cls, v):
        if v is not None and v < 1:
            raise ValueError("总馆藏数量必须大于等于1")
        return v


class BookListQuery(BaseModel):
    page: int = 1
    page_size: int = 10
    keyword: Optional[str] = None
    category_id: Optional[int] = None
