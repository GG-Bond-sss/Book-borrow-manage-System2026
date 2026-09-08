"""图书模块测试。"""
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
from models.category import Category


def setup_function():
    Base.metadata.create_all(bind=test_engine)


def teardown_function():
    Base.metadata.drop_all(bind=test_engine)


def seed_and_get_admin_token():
    db = TestSessionLocal()
    create_test_admin(db)
    db.close()
    return get_auth_token(TestClient(app), "admin", "123456")


def seed_and_get_reader_token():
    db = TestSessionLocal()
    create_test_reader(db)
    db.close()
    return get_auth_token(TestClient(app), "reader1", "123456")


def seed_books():
    """初始化数据，返回图书 id 列表。"""
    db = TestSessionLocal()
    create_test_admin(db)
    cats = create_test_categories(db)
    create_test_books(db, cats)
    db.commit()
    book_ids = [b.id for b in db.query(Book).order_by(Book.id).all()]
    cat_ids = [c.id for c in db.query(Category).order_by(Category.id).all()]
    db.close()
    return book_ids, cat_ids


def test_list_books():
    """测试图书列表。"""
    seed_books()
    client = TestClient(app)
    resp = client.get("/api/books")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 3


def test_list_books_with_search():
    """测试搜索图书。"""
    seed_books()
    client = TestClient(app)
    resp = client.get("/api/books", params={"keyword": "三体"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "三体"


def test_list_books_with_category():
    """测试按分类筛选。"""
    book_ids, cat_ids = seed_books()
    client = TestClient(app)
    resp = client.get("/api/books", params={"category_id": cat_ids[0]})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 1


def test_get_book_detail():
    """测试图书详情。"""
    book_ids, _ = seed_books()
    client = TestClient(app)
    resp = client.get(f"/api/books/{book_ids[0]}")
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "红楼梦"


def test_get_book_not_found():
    """测试获取不存在的图书。"""
    client = TestClient(app)
    resp = client.get("/api/books/9999")
    assert resp.status_code == 404


def test_create_book_success():
    """测试新增图书成功。"""
    _, cat_ids = seed_books()
    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.post("/api/books", data={
        "title": "新书", "author": "作者", "isbn": "9780000000001",
        "category_id": str(cat_ids[0]), "total_count": "3",
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["title"] == "新书"
    assert data["available_count"] == 3


def test_create_book_duplicate_isbn():
    """测试ISBN重复。"""
    book_ids, cat_ids = seed_books()
    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.post("/api/books", data={
        "title": "新书", "author": "作者", "isbn": "9787020002207",
        "category_id": str(cat_ids[0]), "total_count": "3",
    }, headers=auth_headers(token))
    assert resp.status_code == 400


def test_create_book_no_permission():
    """测试读者无权限新增图书。"""
    token = seed_and_get_reader_token()
    client = TestClient(app)
    resp = client.post("/api/books", data={
        "title": "新书", "author": "作者", "isbn": "9780000000001",
        "category_id": "1", "total_count": "3",
    }, headers=auth_headers(token))
    assert resp.status_code == 403


def test_update_book_success():
    """测试编辑图书成功。"""
    book_ids, _ = seed_books()
    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.put(f"/api/books/{book_ids[0]}", data={
        "title": "红楼梦（修订版）",
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    assert "修订版" in resp.json()["data"]["title"]


def test_update_book_total_count_validation():
    """测试BR-08：总馆藏数不能小于已借出数量。"""
    db = TestSessionLocal()
    create_test_admin(db)
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    books[0].available_count = 4  # 5本借出1本
    db.commit()
    book_id = books[0].id
    db.close()

    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.put(f"/api/books/{book_id}", data={"total_count": "0"}, headers=auth_headers(token))
    assert resp.status_code == 400


def test_delete_book_success():
    """测试删除无借阅记录的图书成功。"""
    book_ids, _ = seed_books()
    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.delete(f"/api/books/{book_ids[0]}", headers=auth_headers(token))
    assert resp.status_code == 200


def test_delete_book_with_active_borrow():
    """测试BR-05：有借阅记录的图书不可删除。"""
    db = TestSessionLocal()
    create_test_admin(db)
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    reader = create_test_reader(db)
    from models.borrow_record import BorrowRecord
    from datetime import datetime, timedelta
    record = BorrowRecord(
        user_id=reader.id, book_id=books[0].id,
        borrow_time=datetime.now(), due_time=datetime.now() + timedelta(days=30),
        status="borrowed",
    )
    db.add(record)
    db.commit()
    book_id = books[0].id
    db.close()

    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.delete(f"/api/books/{book_id}", headers=auth_headers(token))
    assert resp.status_code == 400
    assert "未归还" in resp.json()["detail"]


def test_delete_book_not_found():
    """测试删除不存在的图书。"""
    token = seed_and_get_admin_token()
    client = TestClient(app)
    resp = client.delete("/api/books/9999", headers=auth_headers(token))
    assert resp.status_code == 404
