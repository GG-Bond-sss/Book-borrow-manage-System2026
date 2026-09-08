"""借阅模块测试。"""
import os
import sys
from datetime import datetime, timedelta

os.environ["USE_SQLITE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from tests.conftest import (
    create_test_admin, create_test_reader, create_test_categories,
    create_test_books, get_auth_token, auth_headers, TestSessionLocal, test_engine
)
from database import Base
from main import app
from models.borrow_record import BorrowRecord
from models.book import Book


def setup_function():
    Base.metadata.create_all(bind=test_engine)


def teardown_function():
    Base.metadata.drop_all(bind=test_engine)


def seed_env():
    """初始化：返回 (book_ids, reader_created)。"""
    db = TestSessionLocal()
    create_test_admin(db)
    create_test_reader(db)
    cats = create_test_categories(db)
    create_test_books(db, cats)
    db.commit()
    book_ids = [b.id for b in db.query(Book).order_by(Book.id).all()]
    db.close()
    return book_ids


def get_admin_token():
    return get_auth_token(TestClient(app), "admin", "123456")


def get_reader_token():
    return get_auth_token(TestClient(app), "reader1", "123456")


def test_borrow_success():
    """测试借书成功。"""
    book_ids = seed_env()
    token = get_reader_token()
    client = TestClient(app)
    resp = client.post("/api/borrow", json={"book_id": book_ids[0]}, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "borrowed"


def test_borrow_no_available():
    """测试BR-03：可借数量为0时不可借。"""
    db = TestSessionLocal()
    create_test_admin(db)
    create_test_reader(db)
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    books[0].available_count = 0
    db.commit()
    book_id = books[0].id
    db.close()

    token = get_reader_token()
    client = TestClient(app)
    resp = client.post("/api/borrow", json={"book_id": book_id}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert "已借完" in resp.json()["detail"]


def test_borrow_limit_exceeded():
    """测试BR-01：借阅上限5册。"""
    from config import settings
    db = TestSessionLocal()
    create_test_admin(db)
    reader = create_test_reader(db)
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    for i in range(settings.BORROW_LIMIT):
        record = BorrowRecord(
            user_id=reader.id, book_id=books[i % 3].id,
            borrow_time=datetime.now(), due_time=datetime.now() + timedelta(days=30),
            status="borrowed",
        )
        db.add(record)
    db.commit()
    book_id = books[0].id
    db.close()

    token = get_reader_token()
    client = TestClient(app)
    resp = client.post("/api/borrow", json={"book_id": book_id}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert "上限" in resp.json()["detail"]


def test_borrow_with_overdue():
    """测试BR-04：有逾期未还不可再借。"""
    db = TestSessionLocal()
    create_test_admin(db)
    reader = create_test_reader(db)
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    record = BorrowRecord(
        user_id=reader.id, book_id=books[0].id,
        borrow_time=datetime.now() - timedelta(days=40),
        due_time=datetime.now() - timedelta(days=10),
        status="overdue",
    )
    db.add(record)
    db.commit()
    book_id = books[1].id
    db.close()

    token = get_reader_token()
    client = TestClient(app)
    resp = client.post("/api/borrow", json={"book_id": book_id}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert "逾期" in resp.json()["detail"]


def test_borrow_book_not_found():
    """测试借不存在的图书。"""
    seed_env()
    token = get_reader_token()
    client = TestClient(app)
    resp = client.post("/api/borrow", json={"book_id": 9999}, headers=auth_headers(token))
    assert resp.status_code == 404


def test_my_borrows():
    """测试获取我的借阅记录。"""
    db = TestSessionLocal()
    create_test_admin(db)
    reader = create_test_reader(db)
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    record = BorrowRecord(
        user_id=reader.id, book_id=books[0].id,
        borrow_time=datetime.now(), due_time=datetime.now() + timedelta(days=30),
        status="borrowed",
    )
    db.add(record)
    db.commit()
    db.close()

    token = get_reader_token()
    client = TestClient(app)
    resp = client.get("/api/borrow/my", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 1


def test_return_book_success():
    """测试还书成功。"""
    db = TestSessionLocal()
    create_test_admin(db)
    reader = create_test_reader(db)
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    record = BorrowRecord(
        user_id=reader.id, book_id=books[0].id,
        borrow_time=datetime.now(), due_time=datetime.now() + timedelta(days=30),
        status="borrowed",
    )
    db.add(record)
    books[0].available_count -= 1
    db.commit()
    record_id = record.id
    db.close()

    token = get_reader_token()
    client = TestClient(app)
    resp = client.post("/api/borrow/return", json={"record_id": record_id}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "returned"


def test_return_already_returned():
    """测试归还已归还的记录。"""
    db = TestSessionLocal()
    create_test_admin(db)
    reader = create_test_reader(db)
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    record = BorrowRecord(
        user_id=reader.id, book_id=books[0].id,
        borrow_time=datetime.now() - timedelta(days=10),
        due_time=datetime.now() + timedelta(days=20),
        return_time=datetime.now(),
        status="returned",
    )
    db.add(record)
    db.commit()
    record_id = record.id
    db.close()

    token = get_reader_token()
    client = TestClient(app)
    resp = client.post("/api/borrow/return", json={"record_id": record_id}, headers=auth_headers(token))
    assert resp.status_code == 400


def test_return_others_record():
    """测试归还他人借阅记录（无权操作）。"""
    db = TestSessionLocal()
    create_test_admin(db)
    create_test_reader(db)
    from models.user import User
    from services.auth_service import hash_password
    reader2 = User(
        username="reader2", password=hash_password("123456"),
        role="reader", real_name="李四", phone="13900000002", email="r2@t.com",
    )
    db.add(reader2)
    db.commit()
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    record = BorrowRecord(
        user_id=reader2.id, book_id=books[0].id,
        borrow_time=datetime.now(), due_time=datetime.now() + timedelta(days=30),
        status="borrowed",
    )
    db.add(record)
    db.commit()
    record_id = record.id
    db.close()

    token = get_reader_token()
    client = TestClient(app)
    resp = client.post("/api/borrow/return", json={"record_id": record_id}, headers=auth_headers(token))
    assert resp.status_code == 403


def test_all_records_admin():
    """测试管理员查看全部借阅记录。"""
    db = TestSessionLocal()
    create_test_admin(db)
    reader = create_test_reader(db)
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    record = BorrowRecord(
        user_id=reader.id, book_id=books[0].id,
        borrow_time=datetime.now(), due_time=datetime.now() + timedelta(days=30),
        status="borrowed",
    )
    db.add(record)
    db.commit()
    db.close()

    token = get_admin_token()
    client = TestClient(app)
    resp = client.get("/api/borrow/records", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] >= 1


def test_all_records_reader_forbidden():
    """测试读者无权查看全部借阅记录。"""
    seed_env()
    token = get_reader_token()
    client = TestClient(app)
    resp = client.get("/api/borrow/records", headers=auth_headers(token))
    assert resp.status_code == 403


def test_admin_return_success():
    """测试管理员办理归还。"""
    db = TestSessionLocal()
    create_test_admin(db)
    reader = create_test_reader(db)
    cats = create_test_categories(db)
    books = create_test_books(db, cats)
    record = BorrowRecord(
        user_id=reader.id, book_id=books[0].id,
        borrow_time=datetime.now(), due_time=datetime.now() + timedelta(days=30),
        status="borrowed",
    )
    db.add(record)
    books[0].available_count -= 1
    db.commit()
    record_id = record.id
    db.close()

    token = get_admin_token()
    client = TestClient(app)
    resp = client.post("/api/borrow/admin-return", json={"record_id": record_id}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "returned"
