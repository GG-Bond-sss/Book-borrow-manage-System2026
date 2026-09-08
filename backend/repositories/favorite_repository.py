"""收藏数据访问层。"""
from typing import Optional
from sqlalchemy.orm import Session

from models.favorite import Favorite
from repositories.base import BaseRepository


class FavoriteRepository(BaseRepository[Favorite]):
    model = Favorite

    def __init__(self, db: Session):
        super().__init__(db)

    def get_by_user_book(self, user_id: int, book_id: int) -> Optional[Favorite]:
        return (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.book_id == book_id)
            .first()
        )

    def is_favorited(self, user_id: int, book_id: int) -> bool:
        return self.get_by_user_book(user_id, book_id) is not None

    def get_user_favorites(self, user_id: int, page: int = 1, page_size: int = 10) -> tuple:
        query = self.db.query(Favorite).filter(Favorite.user_id == user_id)
        total = query.count()
        items = (
            query.order_by(Favorite.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def delete_favorites_for_book(self, book_id: int) -> int:
        """删除某图书的所有收藏记录（图书删除时级联）。"""
        deleted = (
            self.db.query(Favorite).filter(Favorite.book_id == book_id).delete()
        )
        self.db.flush()
        return deleted
