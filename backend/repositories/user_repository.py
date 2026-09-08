"""用户数据访问层。"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, db: Session):
        super().__init__(db)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def username_exists(self, username: str) -> bool:
        return self.db.query(User).filter(User.username == username).count() > 0

    def get_admins(self) -> List[User]:
        return self.db.query(User).filter(User.role == "admin").all()
