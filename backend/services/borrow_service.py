"""借阅服务层。"""
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from models.book import Book
from models.borrow_record import BorrowRecord
from models.user import User
from repositories.book_repository import BookRepository
from repositories.borrow_record_repository import BorrowRecordRepository


class BorrowService:
    """借阅业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = BorrowRecordRepository(db)
        self.book_repo = BookRepository(db)

    def borrow_book(self, user: User, book_id: int) -> dict:
        """读者借书。

        BR-01: 借阅上限5册
        BR-02: 借期30天
        BR-03: 可借数量为0不可借
        BR-04: 有逾期未还不可再借
        """
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图书不存在",
            )
        # BR-03: 可借数量校验
        if book.available_count <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该书已借完",
            )
        # BR-01: 借阅上限校验
        active_count = self.repo.count_user_active_records(user.id)
        if active_count >= settings.BORROW_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"借阅数量已达上限（{settings.BORROW_LIMIT}册）",
            )
        # BR-04: 逾期未还校验
        if self.repo.has_user_overdue_records(user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您有逾期未还图书，暂不可借阅",
            )

        now = datetime.now()
        due = now + timedelta(days=settings.LOAN_PERIOD_DAYS)
        record = BorrowRecord(
            user_id=user.id,
            book_id=book_id,
            borrow_time=now,
            due_time=due,
            status="borrowed",
            operator_id=None,
        )
        self.repo.save(record)

        # 库存 -1
        book.available_count -= 1
        self.db.commit()

        return record.to_dict()

    def get_my_borrows(self, user: User, page: int = 1, page_size: int = 10,
                       status_filter: str = None) -> dict:
        """获取本人借阅记录（分页）。"""
        # 先刷新逾期状态
        records = self.repo.get_user_active_records(user.id)
        self.repo.refresh_overdue_for_records(records)
        self.db.commit()

        items, total = self.repo.get_user_records(
            user.id, page, page_size, status=status_filter
        )
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": [r.to_dict() for r in items],
        }

    def return_book(self, user: User, record_id: int) -> dict:
        """读者还书。

        BR-10: 逾期不拦截还书
        """
        record = self.repo.get_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="借阅记录不存在",
            )
        if record.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权操作他人借阅记录",
            )
        if record.status == "returned":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该记录已归还",
            )

        # 先刷新逾期状态
        self.repo.refresh_overdue_for_records([record])

        record.status = "returned"
        record.return_time = datetime.now()
        record.operator_id = user.id
        self.repo.save(record)

        # 库存 +1
        book = self.book_repo.get_by_id(record.book_id)
        if book:
            book.available_count += 1
            self.db.commit()

        return record.to_dict()

    def get_all_records(self, page: int = 1, page_size: int = 10,
                        status_filter: str = None, keyword: str = None,
                        book_id: int = None) -> dict:
        """管理员查看全部借阅记录。"""
        # 先全局刷新逾期状态
        self.repo.update_overdue_status()
        self.db.commit()

        items, total = self.repo.get_all_records(
            page, page_size, status=status_filter, keyword=keyword, book_id=book_id
        )
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": [r.to_dict() for r in items],
        }

    def admin_return_book(self, admin: User, record_id: int) -> dict:
        """管理员办理归还。

        BR-10: 逾期不拦截还书
        """
        record = self.repo.get_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="借阅记录不存在",
            )
        if record.status == "returned":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该记录已归还",
            )

        # 先刷新逾期状态
        self.repo.refresh_overdue_for_records([record])

        record.status = "returned"
        record.return_time = datetime.now()
        record.operator_id = admin.id
        self.repo.save(record)

        # 库存 +1
        book = self.book_repo.get_by_id(record.book_id)
        if book:
            book.available_count += 1
            self.db.commit()

        return record.to_dict()
