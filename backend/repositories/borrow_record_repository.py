"""借阅记录数据访问层。"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.borrow_record import BorrowRecord
from repositories.base import BaseRepository


class BorrowRecordRepository(BaseRepository[BorrowRecord]):
    model = BorrowRecord

    def __init__(self, db: Session):
        super().__init__(db)

    def get_user_active_records(self, user_id: int) -> List[BorrowRecord]:
        """获取用户当前借阅中或逾期的记录。"""
        return (
            self.db.query(BorrowRecord)
            .filter(
                BorrowRecord.user_id == user_id,
                BorrowRecord.status.in_(["borrowed", "overdue"]),
            )
            .all()
        )

    def count_user_active_records(self, user_id: int) -> int:
        """统计用户当前借阅中+逾期的记录数。"""
        return (
            self.db.query(BorrowRecord)
            .filter(
                BorrowRecord.user_id == user_id,
                BorrowRecord.status.in_(["borrowed", "overdue"]),
            )
            .count()
        )

    def has_user_overdue_records(self, user_id: int) -> bool:
        """判断用户是否有逾期未还图书。"""
        return (
            self.db.query(BorrowRecord)
            .filter(
                BorrowRecord.user_id == user_id,
                BorrowRecord.status == "overdue",
            )
            .count()
            > 0
        )

    def has_active_records_for_book(self, book_id: int) -> bool:
        """判断图书是否有未归还记录。"""
        return (
            self.db.query(BorrowRecord)
            .filter(
                BorrowRecord.book_id == book_id,
                BorrowRecord.status.in_(["borrowed", "overdue"]),
            )
            .count()
            > 0
        )

    def count_active_records_for_book(self, book_id: int) -> int:
        """统计图书未归还记录数。"""
        return (
            self.db.query(BorrowRecord)
            .filter(
                BorrowRecord.book_id == book_id,
                BorrowRecord.status.in_(["borrowed", "overdue"]),
            )
            .count()
        )

    def get_user_records(
        self, user_id: int, page: int = 1, page_size: int = 10, status: str = None
    ) -> tuple:
        """获取用户借阅记录（分页）。"""
        query = self.db.query(BorrowRecord).filter(BorrowRecord.user_id == user_id)
        if status:
            query = query.filter(BorrowRecord.status == status)
        total = query.count()
        items = (
            query.order_by(BorrowRecord.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_all_records(
        self,
        page: int = 1,
        page_size: int = 10,
        status: str = None,
        keyword: str = None,
        book_id: int = None,
    ) -> tuple:
        """获取全部借阅记录（管理员）。"""
        query = self.db.query(BorrowRecord)
        if status:
            query = query.filter(BorrowRecord.status == status)
        if book_id:
            query = query.filter(BorrowRecord.book_id == book_id)
        if keyword:
            # 需要联表查询用户名/姓名/书名
            from models.user import User
            from models.book import Book

            query = query.join(User, BorrowRecord.user_id == User.id).join(
                Book, BorrowRecord.book_id == Book.id
            )
            query = query.filter(
                or_(
                    User.username.contains(keyword),
                    User.real_name.contains(keyword),
                    Book.title.contains(keyword),
                )
            )
        total = query.count()
        items = (
            query.order_by(BorrowRecord.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def update_overdue_status(self) -> int:
        """将应还时间已过且未归还的记录标记为逾期。返回更新行数。"""
        from datetime import datetime

        now = datetime.now()
        records = (
            self.db.query(BorrowRecord)
            .filter(
                BorrowRecord.status == "borrowed",
                BorrowRecord.due_time < now,
            )
            .all()
        )
        for record in records:
            record.status = "overdue"
        self.db.flush()
        return len(records)

    def refresh_overdue_for_records(self, records: List[BorrowRecord]) -> None:
        """为传入的记录刷新逾期状态。"""
        from datetime import datetime

        now = datetime.now()
        for record in records:
            if record.status == "borrowed" and record.due_time < now:
                record.status = "overdue"
        self.db.flush()
