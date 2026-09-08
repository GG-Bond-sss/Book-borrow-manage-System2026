"""分类数据访问层。"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.category import Category
from models.book import Book
from repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    model = Category

    def __init__(self, db: Session):
        super().__init__(db)

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.name == name).first()

    def name_exists(self, name: str, exclude_id: int = None) -> bool:
        query = self.db.query(Category).filter(Category.name == name)
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
        return query.count() > 0

    def get_book_count(self, category_id: int) -> int:
        return self.db.query(func.count(Book.id)).filter(Book.category_id == category_id).scalar() or 0

    def get_all_with_count(self) -> list:
        categories = self.db.query(Category).order_by(Category.id).all()
        result = []
        for cat in categories:
            count = self.get_book_count(cat.id)
            result.append((cat, count))
        return result
