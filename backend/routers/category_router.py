"""分类路由。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import require_admin, get_current_user
from models.user import User
from response import success
from schemas.category import CategoryCreateRequest, CategoryUpdateRequest
from services.category_service import CategoryService

router = APIRouter(prefix="/api/categories", tags=["分类管理"])


@router.get("")
def list_categories(db: Session = Depends(get_db)):
    """分类列表。"""
    service = CategoryService(db)
    result = service.list_categories()
    return success(data=result)


@router.post("")
def create_category(
    req: CategoryCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """新增分类（管理员）。"""
    service = CategoryService(db)
    result = service.create_category(req.name)
    return success(data=result, message="新增成功")


@router.put("/{category_id}")
def update_category(
    category_id: int,
    req: CategoryUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """修改分类（管理员）。"""
    service = CategoryService(db)
    result = service.update_category(category_id, req.name)
    return success(data=result, message="修改成功")


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """删除分类（管理员）。"""
    service = CategoryService(db)
    service.delete_category(category_id)
    return success(message="删除成功")
