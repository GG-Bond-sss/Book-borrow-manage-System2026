"""用户模型。"""
from sqlalchemy import Column, String, Enum, DateTime, func

from database import Base, BigIntVariant


class User(Base):
    """用户表（管理员与读者）。"""

    __tablename__ = "user"

    id = Column(BigIntVariant, primary_key=True, autoincrement=True, comment="用户唯一标识")
    username = Column(String(50), unique=True, nullable=False, comment="登录用户名")
    password = Column(String(100), nullable=False, comment="密码（bcrypt 哈希）")
    role = Column(Enum("admin", "reader"), nullable=False, default="reader", comment="角色")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    phone = Column(String(20), nullable=False, comment="手机号（必填）")
    email = Column(String(100), nullable=False, comment="邮箱（必填）")
    contact = Column(String(200), nullable=True, comment="备用联系方式")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "real_name": self.real_name,
            "phone": self.phone,
            "email": self.email,
            "contact": self.contact,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }
