"""分类模型。"""
from sqlalchemy import Column, String, DateTime, func

from database import Base, BigIntVariant


class Category(Base):
    """图书分类表。"""

    __tablename__ = "category"

    id = Column(BigIntVariant, primary_key=True, autoincrement=True, comment="分类唯一标识")
    name = Column(String(50), unique=True, nullable=False, comment="分类名称")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    def to_dict(self, book_count: int = 0) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "book_count": book_count,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }
