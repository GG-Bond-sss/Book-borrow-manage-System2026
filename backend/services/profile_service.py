"""个人资料服务层。"""
import re
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User
from repositories.user_repository import UserRepository
from services.auth_service import verify_password, hash_password


class ProfileService:
    """个人资料业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def get_profile(self, user: User) -> dict:
        """获取个人资料。"""
        return user.to_dict()

    def update_profile(self, user: User, phone: str, email: str) -> dict:
        """修改手机号和邮箱。

        BR-15: 用户名和姓名不可修改
        BR-16: 手机号11位、邮箱含@
        """
        if not re.match(r"^\d{11}$", phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号必须为11位数字",
            )
        if "@" not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱格式不正确",
            )
        user.phone = phone
        user.email = email
        self.repo.save(user)
        return user.to_dict()

    def change_password(self, user: User, old_password: str,
                         new_password: str, confirm_password: str) -> dict:
        """修改密码。

        BR-18: 需验证原密码
        BR-19: 新密码6-20位，两次一致
        """
        # BR-18: 验证原密码
        if not verify_password(old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码不正确",
            )
        # BR-19: 新密码长度校验
        if len(new_password) < 6 or len(new_password) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码长度必须为6-20位",
            )
        # BR-19: 两次密码一致校验
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="两次输入的密码不一致",
            )
        # 新密码不能与原密码相同
        if verify_password(new_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不能与原密码相同",
            )

        user.password = hash_password(new_password)
        self.repo.save(user)
        return {"message": "密码修改成功"}
