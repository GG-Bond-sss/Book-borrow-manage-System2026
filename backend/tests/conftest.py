"""测试配置与夹具。"""
import os
import sys

# 设置使用 SQLite 测试环境
os.environ["USE_SQLITE"] = "1"

# 将 backend 目录加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models.user import User
from models.category import Category
from models.book import Book
from models.borrow_record import BorrowRecord
from services.auth_service import hash_password

# 创建 SQLite 内存数据库
TEST_SQLITE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """测试用数据库会话。"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """每个测试函数使用独立的数据库会话。"""
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """测试客户端。"""
    Base.metadata.create_all(bind=test_engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=test_engine)


def create_test_admin(db):
    """创建测试管理员。"""
    admin = User(
        username="admin",
        password=hash_password("123456"),
        role="admin",
        real_name="管理员",
        phone="13800000000",
        email="admin@test.com",
    )
    db.add(admin)
    db.commit()
    return admin


def create_test_reader(db, username="reader1"):
    """创建测试读者。"""
    reader = User(
        username=username,
        password=hash_password("123456"),
        role="reader",
        real_name="张三",
        phone="13900000001",
        email="reader1@test.com",
    )
    db.add(reader)
    db.commit()
    return reader


def create_test_categories(db):
    """创建测试分类。"""
    cats = []
    for name in ["文学", "科技", "历史"]:
        cat = Category(name=name)
        db.add(cat)
        cats.append(cat)
    db.commit()
    return cats


def create_test_books(db, categories):
    """创建测试图书。"""
    books = []
    data = [
        ("红楼梦", "曹雪芹", "9787020002207", categories[0].id, 5, 5),
        ("三体", "刘慈欣", "9787536692930", categories[1].id, 3, 3),
        ("明朝那些事儿", "当年明月", "9787540461188", categories[2].id, 4, 4),
    ]
    for title, author, isbn, cat_id, total, avail in data:
        book = Book(
            title=title, author=author, isbn=isbn,
            category_id=cat_id, total_count=total, available_count=avail,
        )
        db.add(book)
        books.append(book)
    db.commit()
    return books


def get_auth_token(client, username, password):
    """获取认证 token。"""
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    return data["data"]["token"]


def auth_headers(token):
    """构建认证请求头。"""
    return {"Authorization": f"Bearer {token}"}
