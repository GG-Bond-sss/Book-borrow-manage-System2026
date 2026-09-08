"""收藏记录模型。"""
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from database import Base, BigIntVariant


class Favorite(Base):
    """收藏记录表。"""

    __tablename__ = "favorite"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uk_user_book"),
    )

    id = Column(BigIntVariant, primary_key=True, autoincrement=True, comment="收藏记录唯一标识")
    user_id = Column(BigIntVariant, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="收藏读者 ID")
    book_id = Column(BigIntVariant, ForeignKey("book.id", ondelete="CASCADE"), nullable=False, comment="被收藏图书 ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="收藏时间")

    user = relationship("User", lazy="joined")
    book = relationship("Book", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "book": self.book.to_dict() if self.book else None,
        }
