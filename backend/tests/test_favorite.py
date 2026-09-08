"""收藏模块测试。"""
import os
import sys

os.environ["USE_SQLITE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from tests.conftest import (
    create_test_admin, create_test_reader, create_test_categories,
    create_test_books, get_auth_token, auth_headers, TestSessionLocal, test_engine
)
from database import Base
from main import app
from models.book import Book


def setup_function():
    Base.metadata.create_all(bind=test_engine)


def teardown_function():
    Base.metadata.drop_all(bind=test_engine)


def seed_and_get_token():
    db = TestSessionLocal()
    create_test_admin(db)
    create_test_reader(db)
    cats = create_test_categories(db)
    create_test_books(db, cats)
    db.commit()
    book_ids = [b.id for b in db.query(Book).order_by(Book.id).all()]
    db.close()
    token = get_auth_token(TestClient(app), "reader1", "123456")
    return book_ids, token


def test_toggle_favorite_add():
    """测试添加收藏。"""
    book_ids, token = seed_and_get_token()
    client = TestClient(app)
    resp = client.post("/api/favorites/toggle", json={"book_id": book_ids[0]}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["data"]["favorited"] is True


def test_toggle_favorite_remove():
    """测试取消收藏（切换）。"""
    book_ids, token = seed_and_get_token()
    client = TestClient(app)
    client.post("/api/favorites/toggle", json={"book_id": book_ids[0]}, headers=auth_headers(token))
    resp = client.post("/api/favorites/toggle", json={"book_id": book_ids[0]}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["data"]["favorited"] is False


def test_toggle_favorite_book_not_found():
    """测试收藏不存在的图书。"""
    _, token = seed_and_get_token()
    client = TestClient(app)
    resp = client.post("/api/favorites/toggle", json={"book_id": 9999}, headers=auth_headers(token))
    assert resp.status_code == 404


def test_my_favorites():
    """测试我的收藏列表。"""
    book_ids, token = seed_and_get_token()
    client = TestClient(app)
    client.post("/api/favorites/toggle", json={"book_id": book_ids[0]}, headers=auth_headers(token))
    resp = client.get("/api/favorites", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 1


def test_my_favorites_empty():
    """测试空收藏列表。"""
    _, token = seed_and_get_token()
    client = TestClient(app)
    resp = client.get("/api/favorites", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 0


def test_favorites_require_auth():
    """测试未登录访问收藏。"""
    client = TestClient(app)
    resp = client.get("/api/favorites")
    assert resp.status_code == 401
