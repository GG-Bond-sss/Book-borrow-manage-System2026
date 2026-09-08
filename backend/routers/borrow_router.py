"""借阅路由。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user, require_admin, require_reader
from models.user import User
from response import success
from schemas.borrow import BorrowRequest, ReturnRequest
from services.borrow_service import BorrowService

router = APIRouter(prefix="/api/borrow", tags=["借阅管理"])


@router.post("")
def borrow_book(
    req: BorrowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reader),
):
    """读者借书。"""
    service = BorrowService(db)
    result = service.borrow_book(current_user, req.book_id)
    return success(data=result, message="借阅成功")


@router.get("/my")
def my_borrows(
    page: int = 1,
    page_size: int = 10,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reader),
):
    """我的借阅记录。"""
    service = BorrowService(db)
    result = service.get_my_borrows(current_user, page, page_size, status)
    return success(data=result)


@router.post("/return")
def return_book(
    req: ReturnRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reader),
):
    """读者还书。"""
    service = BorrowService(db)
    result = service.return_book(current_user, req.record_id)
    return success(data=result, message="归还成功")


@router.get("/records")
def all_records(
    page: int = 1,
    page_size: int = 10,
    status: str = None,
    keyword: str = None,
    book_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """管理员查看全部借阅记录。"""
    service = BorrowService(db)
    result = service.get_all_records(page, page_size, status, keyword, book_id)
    return success(data=result)


@router.post("/admin-return")
def admin_return(
    req: ReturnRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """管理员办理归还。"""
    service = BorrowService(db)
    result = service.admin_return_book(current_user, req.record_id)
    return success(data=result, message="归还成功")
