"""个人资料路由。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models.user import User
from response import success
from schemas.profile import ProfileUpdateRequest, ChangePasswordRequest
from services.profile_service import ProfileService

router = APIRouter(prefix="/api/profile", tags=["个人资料"])


@router.get("")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取个人资料。"""
    service = ProfileService(db)
    result = service.get_profile(current_user)
    return success(data=result)


@router.put("")
def update_profile(
    req: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """修改手机号和邮箱。"""
    service = ProfileService(db)
    result = service.update_profile(current_user, req.phone, req.email)
    return success(data=result, message="修改成功")


@router.put("/password")
def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """修改密码。"""
    service = ProfileService(db)
    result = service.change_password(
        current_user, req.old_password, req.new_password, req.confirm_password
    )
    return success(data=result, message="密码修改成功")
