"""认证路由。"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models.user import User
from response import success, error
from schemas.auth import LoginRequest, RegisterRequest
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录。"""
    service = AuthService(db)
    result = service.login(req.username, req.password)
    return success(data=result, message="登录成功")


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """读者注册。"""
    service = AuthService(db)
    result = service.register(
        req.username, req.password, req.confirm_password,
        req.real_name, req.phone, req.email,
    )
    return success(data=result, message="注册成功")


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息。"""
    return success(data={
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "real_name": current_user.real_name,
        "phone": current_user.phone,
        "email": current_user.email,
        "contact": current_user.contact,
        "created_at": current_user.created_at.strftime("%Y-%m-%d %H:%M:%S") if current_user.created_at else None,
    })


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """退出登录（JWT 无状态，前端清除即可）。"""
    return success(message="退出成功")
