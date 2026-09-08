"""分类模块测试。"""
import os
import sys

os.environ["USE_SQLITE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from tests.conftest import (
    create_test_admin, create_test_reader, create_test_categories,
    get_auth_token, auth_headers, TestSessionLocal, test_engine
)
from database import Base
from main import app


def setup_function():
    Base.metadata.create_all(bind=test_engine)


def teardown_function():
    Base.metadata.drop_all(bind=test_engine)


def get_admin_token():
    db = TestSessionLocal()
    create_test_admin(db)
    db.close()
    client = TestClient(app)
    return get_auth_token(client, "admin", "123456")


def get_reader_token():
    db = TestSessionLocal()
    create_test_reader(db)
    db.close()
    client = TestClient(app)
    return get_auth_token(client, "reader1", "123456")


def test_list_categories():
    """测试分类列表。"""
    db = TestSessionLocal()
    create_test_admin(db)
    create_test_categories(db)
    db.close()

    client = TestClient(app)
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert len(data["data"]) == 3


def test_create_category_success():
    """测试新增分类成功。"""
    token = get_admin_token()
    client = TestClient(app)
    resp = client.post("/api/categories", json={"name": "科幻"}, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["data"]["name"] == "科幻"


def test_create_category_duplicate():
    """测试重复分类名。"""
    db = TestSessionLocal()
    create_test_admin(db)
    create_test_categories(db)
    db.close()

    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.post("/api/categories", json={"name": "文学"}, headers=auth_headers(token))
    assert resp.status_code == 400


def test_create_category_no_permission():
    """测试读者无权限新增分类。"""
    token = get_reader_token()
    client = TestClient(app)
    resp = client.post("/api/categories", json={"name": "科幻"}, headers=auth_headers(token))
    assert resp.status_code == 403


def test_update_category_success():
    """测试修改分类成功。"""
    db = TestSessionLocal()
    create_test_admin(db)
    cats = create_test_categories(db)
    cat_id = cats[0].id
    db.close()

    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.put(f"/api/categories/{cat_id}", json={"name": "文学小说"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "文学小说"


def test_update_category_duplicate_name():
    """测试修改分类名为已存在名称。"""
    db = TestSessionLocal()
    create_test_admin(db)
    cats = create_test_categories(db)
    cat_id = cats[0].id
    db.close()

    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.put(f"/api/categories/{cat_id}", json={"name": "科技"}, headers=auth_headers(token))
    assert resp.status_code == 400


def test_delete_category_success():
    """测试删除空分类成功。"""
    db = TestSessionLocal()
    create_test_admin(db)
    cats = create_test_categories(db)
    cat_id = cats[0].id  # 文学，无图书
    db.close()

    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.delete(f"/api/categories/{cat_id}", headers=auth_headers(token))
    assert resp.status_code == 200


def test_delete_category_with_books():
    """测试删除有图书的分类（BR-11）。"""
    db = TestSessionLocal()
    create_test_admin(db)
    from tests.conftest import create_test_books
    cats = create_test_categories(db)
    create_test_books(db, cats)
    cat_id = cats[0].id  # 文学，有红楼梦
    db.close()

    token = get_auth_token(TestClient(app), "admin", "123456")
    client = TestClient(app)
    resp = client.delete(f"/api/categories/{cat_id}", headers=auth_headers(token))
    assert resp.status_code == 400
    assert "无法删除" in resp.json()["detail"]


def test_delete_category_not_found():
    """测试删除不存在的分类。"""
    token = get_admin_token()
    client = TestClient(app)
    resp = client.delete("/api/categories/9999", headers=auth_headers(token))
    assert resp.status_code == 404
