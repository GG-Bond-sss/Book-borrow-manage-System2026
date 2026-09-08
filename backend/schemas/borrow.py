"""借阅相关 Pydantic 模型。"""
from pydantic import BaseModel
from typing import Optional


class BorrowRequest(BaseModel):
    book_id: int


class ReturnRequest(BaseModel):
    record_id: int


class BorrowListQuery(BaseModel):
    page: int = 1
    page_size: int = 10
    status: Optional[str] = None
    keyword: Optional[str] = None  # 读者或图书关键词
    book_id: Optional[int] = None
