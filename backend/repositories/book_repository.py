"""图书数据访问层。"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.book import Book
from repositories.base import BaseRepository


class BookRepository(BaseRepository[Book]):
    model = Book

    def __init__(self, db: Session):
        super().__init__(db)

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.db.query(Book).filter(Book.isbn == isbn).first()

    def isbn_exists(self, isbn: str, exclude_id: int = None) -> bool:
        query = self.db.query(Book).filter(Book.isbn == isbn)
        if exclude_id:
            query = query.filter(Book.id != exclude_id)
        return query.count() > 0

    def search(
        self,
        keyword: str = None,
        category_id: int = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple:
        query = self.db.query(Book)
        if keyword:
            query = query.filter(
                or_(
                    Book.title.contains(keyword),
                    Book.author.contains(keyword),
                    Book.isbn.contains(keyword),
                )
            )
        if category_id:
            query = query.filter(Book.category_id == category_id)
        total = query.count()
        items = query.order_by(Book.id).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get_category_books(self, category_id: int) -> List[Book]:
        return self.db.query(Book).filter(Book.category_id == category_id).all()
