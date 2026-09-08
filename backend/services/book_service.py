"""图书服务层。"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.book import Book
from repositories.book_repository import BookRepository
from repositories.borrow_record_repository import BorrowRecordRepository
from repositories.favorite_repository import FavoriteRepository


class BookService:
    """图书业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = BookRepository(db)
        self.borrow_repo = BorrowRecordRepository(db)
        self.fav_repo = FavoriteRepository(db)

    def list_books(self, page: int = 1, page_size: int = 10,
                   keyword: str = None, category_id: int = None) -> dict:
        """图书列表（分页+搜索+分类筛选）。"""
        items, total = self.repo.search(keyword, category_id, page, page_size)
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": [b.to_dict() for b in items],
        }

    def get_book(self, book_id: int) -> dict:
        """图书详情。"""
        book = self.repo.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图书不存在",
            )
        return book.to_dict()

    def create_book(self, title: str, author: str, isbn: str, category_id: int,
                    publisher: str = None, publish_year: int = None,
                    total_count: int = 1, summary: str = None,
                    cover_url: str = None) -> dict:
        """新增图书。"""
        if self.repo.isbn_exists(isbn):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISBN 已存在，不可重复添加",
            )
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            category_id=category_id,
            publisher=publisher,
            publish_year=publish_year,
            total_count=total_count,
            available_count=total_count,  # 可借数量=总馆藏
            summary=summary,
            cover_url=cover_url,
        )
        self.repo.save(book)
        return book.to_dict()

    def update_book(self, book_id: int, **kwargs) -> dict:
        """编辑图书。

        BR-08: 调整总馆藏数时，新总数 >= 已借出数量（total - available）方可保存。
        """
        book = self.repo.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图书不存在",
            )

        # ISBN 唯一性校验
        if "isbn" in kwargs and kwargs["isbn"] and kwargs["isbn"] != book.isbn:
            if self.repo.isbn_exists(kwargs["isbn"], exclude_id=book_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ISBN 已存在",
                )

        # BR-08: 总馆藏数联动校验
        if "total_count" in kwargs and kwargs["total_count"] is not None:
            new_total = kwargs["total_count"]
            borrowed = book.total_count - book.available_count
            if new_total < borrowed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"总馆藏数量不能小于已借出数量（当前已借出 {borrowed} 册）",
                )
            # 联动可借数量
            book.available_count = new_total - borrowed

        # 更新字段
        for key, value in kwargs.items():
            if value is not None and hasattr(book, key):
                setattr(book, key, value)

        self.repo.save(book)
        return book.to_dict()

    def delete_book(self, book_id: int) -> None:
        """删除图书。

        BR-05: 有借阅中/逾期记录时禁止删除。
        BR-14: 删除图书时级联删除收藏记录。
        """
        book = self.repo.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图书不存在",
            )
        active_count = self.borrow_repo.count_active_records_for_book(book_id)
        if active_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该图书尚有 {active_count} 册未归还，无法删除",
            )
        # 级联删除收藏记录
        self.fav_repo.delete_favorites_for_book(book_id)
        self.repo.delete(book)
        self.db.commit()
