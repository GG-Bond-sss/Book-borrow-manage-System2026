"""图书模型。"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from database import Base, BigIntVariant


class Book(Base):
    """图书表。"""

    __tablename__ = "book"

    id = Column(BigIntVariant, primary_key=True, autoincrement=True, comment="图书唯一标识")
    title = Column(String(200), nullable=False, comment="书名")
    author = Column(String(100), nullable=False, comment="作者")
    isbn = Column(String(20), unique=True, nullable=False, comment="ISBN 编号")
    category_id = Column(BigIntVariant, ForeignKey("category.id", ondelete="RESTRICT"), nullable=False, comment="分类 ID")
    publisher = Column(String(100), nullable=True, comment="出版社")
    publish_year = Column(Integer, nullable=True, comment="出版年份")
    total_count = Column(Integer, nullable=False, default=1, comment="总馆藏数量")
    available_count = Column(Integer, nullable=False, default=1, comment="可借数量")
    summary = Column(Text, nullable=True, comment="简介")
    cover_url = Column(String(500), nullable=True, comment="封面图片地址")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    category = relationship("Category", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "publisher": self.publisher,
            "publish_year": self.publish_year,
            "total_count": self.total_count,
            "available_count": self.available_count,
            "summary": self.summary,
            "cover_url": self.cover_url,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }
