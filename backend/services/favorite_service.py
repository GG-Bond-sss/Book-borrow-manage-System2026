"""收藏服务层。"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.favorite import Favorite
from repositories.book_repository import BookRepository
from repositories.favorite_repository import FavoriteRepository


class FavoriteService:
    """收藏业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = FavoriteRepository(db)
        self.book_repo = BookRepository(db)

    def toggle_favorite(self, user_id: int, book_id: int) -> dict:
        """切换收藏状态（BR-13）。"""
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图书不存在",
            )
        existing = self.repo.get_by_user_book(user_id, book_id)
        if existing:
            self.repo.delete(existing)
            self.db.commit()
            return {"favorited": False, "message": "已取消收藏"}
        else:
            favorite = Favorite(user_id=user_id, book_id=book_id)
            self.repo.save(favorite)
            return {"favorited": True, "message": "收藏成功"}

    def get_my_favorites(self, user_id: int, page: int = 1, page_size: int = 10) -> dict:
        """获取我的收藏列表。"""
        items, total = self.repo.get_user_favorites(user_id, page, page_size)
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": [f.to_dict() for f in items],
        }

    def is_favorited(self, user_id: int, book_id: int) -> bool:
        return self.repo.is_favorited(user_id, book_id)
