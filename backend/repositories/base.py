"""Repository 基类。"""
from typing import TypeVar, Generic, Optional, List
from sqlalchemy.orm import Session
from database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Repository 基类，提供通用 CRUD 操作。"""

    model: ModelT = None

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelT]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[ModelT]:
        return self.db.query(self.model).all()

    def create(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelT) -> ModelT:
        self.db.merge(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.flush()

    def save(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
