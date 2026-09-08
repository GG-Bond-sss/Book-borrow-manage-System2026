"""图书路由。"""
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user, require_admin
from models.user import User
from response import success, error
from services.book_service import BookService

router = APIRouter(prefix="/api/books", tags=["图书管理"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
ALLOWED_EXTENSIONS = {".jpg", ".png"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


@router.get("")
def list_books(
    page: int = 1,
    page_size: int = 10,
    keyword: str = None,
    category_id: int = None,
    db: Session = Depends(get_db),
):
    """图书列表（分页+搜索+分类筛选）。"""
    service = BookService(db)
    result = service.list_books(page, page_size, keyword, category_id)
    return success(data=result)


@router.get("/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    """图书详情。"""
    service = BookService(db)
    result = service.get_book(book_id)
    return success(data=result)


@router.post("")
def create_book(
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    category_id: int = Form(...),
    publisher: str = Form(None),
    publish_year: int = Form(None),
    total_count: int = Form(1),
    summary: str = Form(None),
    cover_url: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """新增图书（管理员）。"""
    service = BookService(db)
    result = service.create_book(
        title=title, author=author, isbn=isbn, category_id=category_id,
        publisher=publisher, publish_year=publish_year,
        total_count=total_count, summary=summary, cover_url=cover_url,
    )
    return success(data=result, message="新增成功")


@router.put("/{book_id}")
def update_book(
    book_id: int,
    title: str = Form(None),
    author: str = Form(None),
    isbn: str = Form(None),
    category_id: int = Form(None),
    publisher: str = Form(None),
    publish_year: int = Form(None),
    total_count: int = Form(None),
    summary: str = Form(None),
    cover_url: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """编辑图书（管理员）。"""
    service = BookService(db)
    kwargs = {k: v for k, v in locals().items()
              if k not in ["book_id", "db", "current_user", "service"] and v is not None}
    result = service.update_book(book_id, **kwargs)
    return success(data=result, message="修改成功")


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(require_admin)):
    """删除图书（管理员）。"""
    service = BookService(db)
    service.delete_book(book_id)
    return success(message="删除成功")


@router.post("/upload-cover")
async def upload_cover(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
):
    """上传图书封面图片（管理员）。

    BR-12: 仅支持 jpg/png，<= 2MB
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return error(message="仅支持 jpg/png 格式", code=400)

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return error(message="文件大小不能超过 2MB", code=400)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    cover_url = f"/uploads/{filename}"
    return success(data={"cover_url": cover_url}, message="上传成功")
