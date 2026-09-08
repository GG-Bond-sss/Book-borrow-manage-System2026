"""分类服务层。"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.category import Category
from repositories.category_repository import CategoryRepository


class CategoryService:
    """分类业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = CategoryRepository(db)

    def list_categories(self) -> list:
        """获取全部分类（含图书数量）。"""
        result = self.repo.get_all_with_count()
        return [cat.to_dict(book_count=count) for cat, count in result]

    def create_category(self, name: str) -> dict:
        """新增分类。"""
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称不能为空",
            )
        if self.repo.name_exists(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称已存在",
            )
        category = Category(name=name)
        self.repo.save(category)
        return category.to_dict(book_count=0)

    def update_category(self, category_id: int, name: str) -> dict:
        """修改分类。"""
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在",
            )
        if self.repo.name_exists(name, exclude_id=category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称已存在",
            )
        category.name = name
        self.repo.save(category)
        book_count = self.repo.get_book_count(category_id)
        return category.to_dict(book_count=book_count)

    def delete_category(self, category_id: int) -> None:
        """删除分类（BR-11: 有图书时禁止删除）。"""
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在",
            )
        book_count = self.repo.get_book_count(category_id)
        if book_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该分类下有 {book_count} 本图书，无法删除",
            )
        self.repo.delete(category)
        self.db.commit()
