"""认证服务层。"""
from datetime import datetime, timezone
from fastapi import HTTPException, status

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config import settings
from deps import create_access_token
from models.user import User
from repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class AuthService:
    """认证业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def login(self, username: str, password: str) -> dict:
        """用户登录，返回 token 和用户信息。"""
        user = self.repo.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名或密码错误",
            )
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名或密码错误",
            )
        token = create_access_token(
            {"sub": user.username, "role": user.role, "uid": user.id}
        )
        return {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "real_name": user.real_name,
                "phone": user.phone,
                "email": user.email,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None,
            },
        }

    def register(self, username: str, password: str, confirm_password: str,
                 real_name: str, phone: str, email: str) -> dict:
        """读者注册。"""
        # 校验密码长度
        if len(password) < 6 or len(password) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码长度必须为6-20位",
            )
        if password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="两次输入的密码不一致",
            )
        # 校验用户名
        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名不能为空",
            )
        if self.repo.username_exists(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在",
            )
        # 校验真实姓名
        if not real_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="姓名不能为空",
            )
        # 校验手机号
        import re
        if not re.match(r"^\d{11}$", phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号必须为11位数字",
            )
        # 校验邮箱
        if "@" not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱格式不正确",
            )
        # 创建用户，角色固定为 reader
        user = User(
            username=username,
            password=hash_password(password),
            role="reader",
            real_name=real_name,
            phone=phone,
            email=email,
        )
        self.repo.save(user)
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "real_name": user.real_name,
        }

    def get_current_user_info(self, user: User) -> dict:
        """获取当前用户信息。"""
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "real_name": user.real_name,
            "phone": user.phone,
            "email": user.email,
            "contact": user.contact,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None,
        }
