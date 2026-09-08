"""借阅记录模型。"""
from sqlalchemy import Column, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship

from database import Base, BigIntVariant


class BorrowRecord(Base):
    """借阅记录表。"""

    __tablename__ = "borrow_record"

    id = Column(BigIntVariant, primary_key=True, autoincrement=True, comment="记录唯一标识")
    user_id = Column(BigIntVariant, ForeignKey("user.id", ondelete="RESTRICT"), nullable=False, comment="借阅读者 ID")
    book_id = Column(BigIntVariant, ForeignKey("book.id", ondelete="RESTRICT"), nullable=False, comment="所借图书 ID")
    borrow_time = Column(DateTime, nullable=False, comment="借出时间")
    due_time = Column(DateTime, nullable=False, comment="应还时间")
    return_time = Column(DateTime, nullable=True, comment="实际归还时间")
    status = Column(
        Enum("borrowed", "returned", "overdue"),
        nullable=False,
        default="borrowed",
        comment="状态：borrowed 借阅中 / returned 已归还 / overdue 逾期",
    )
    operator_id = Column(BigIntVariant, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, comment="办理归还操作人 ID")

    user = relationship("User", foreign_keys=[user_id], lazy="joined")
    book = relationship("Book", foreign_keys=[book_id], lazy="joined")
    operator = relationship("User", foreign_keys=[operator_id], lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "real_name": self.user.real_name if self.user else None,
            "book_id": self.book_id,
            "book_title": self.book.title if self.book else None,
            "isbn": self.book.isbn if self.book else None,
            "borrow_time": self.borrow_time.strftime("%Y-%m-%d %H:%M:%S") if self.borrow_time else None,
            "due_time": self.due_time.strftime("%Y-%m-%d %H:%M:%S") if self.due_time else None,
            "return_time": self.return_time.strftime("%Y-%m-%d %H:%M:%S") if self.return_time else None,
            "status": self.status,
            "operator_id": self.operator_id,
            "operator_name": self.operator.real_name if self.operator else None,
        }
