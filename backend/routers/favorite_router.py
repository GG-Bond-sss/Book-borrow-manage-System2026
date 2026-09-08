"""收藏路由。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import require_reader
from models.user import User
from response import success
from schemas.favorite import FavoriteToggleRequest
from services.favorite_service import FavoriteService

router = APIRouter(prefix="/api/favorites", tags=["收藏管理"])


@router.post("/toggle")
def toggle_favorite(
    req: FavoriteToggleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reader),
):
    """切换收藏状态。"""
    service = FavoriteService(db)
    result = service.toggle_favorite(current_user.id, req.book_id)
    return success(data=result)


@router.get("")
def my_favorites(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reader),
):
    """我的收藏列表。"""
    service = FavoriteService(db)
    result = service.get_my_favorites(current_user.id, page, page_size)
    return success(data=result)
